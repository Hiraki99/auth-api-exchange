from flask import Flask, request, redirect, jsonify, send_from_directory, render_template, session
from flask import flash
from datetime import datetime
from datetime import timedelta
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_mail import Mail, Message
from AuthAPI import app, db, celery, config, common
from AuthAPI import jwt, blacklist, blacklist_token, mail, serializer
from AuthAPI.controller import process
import traceback
import uuid
import random
import os
import requests
# Initialize models
from AuthAPI.model.user import User
from AuthAPI.model.role import Role
from AuthAPI.model.kyc import Kyc

from AuthAPI.model.permission import Permission
from AuthAPI import redis_client


@app.route('/login', methods=['POST'])
def check_login():
    """ check user login """
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        user: User = User.query.filter_by(username=username).first()
        if (not user):
            return jsonify({'status': 0, 'message': 'Dont Existed User'})

        if(user.confirmed is False):
            return jsonify({'status': -1, 'message': 'User dont active '})
        
        # Check Valid hash password
        if user.verify_password(password):  # please recheck verify password
            # check again, why unused variable Role ?
            permission = Role.get_permission_by_role(user.role)
            data = {
                'status': 1,
                'role': user.role,
                'permission':permission,
                'user_name': user.username,
                'user_id': user.id
            }
            expires = timedelta(seconds=172800)
            access_token = create_access_token(data)
            print(access_token)
            return jsonify({
                'status': 1,
                'access_token': access_token,
                'exp': expires.total_seconds()
            })
        else:
            return jsonify({'status': 0, 'message': 'Invalid Password'})
    except:
        traceback.print_exc()
        return jsonify({'status': 0, 'message': 'Invalid Username or Password'})


@app.route('/logout', methods=['POST','GET'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    
    blacklist.add(jti)
    redis_client.set(jti, datetime.now().isoformat())
    return jsonify({"msg": "Successfully logged out"})

    # return jsonify({"msg": "Successfully logged out"}), 200


@app.route('/update-user', methods=['POST'])
@jwt_required
def update_user():
    """ update user """
    try:
        user_id = request.json.get('user_id')
        email = request.json.get('email')
        phone = request.json.get('phone')
        user = User.query.filter_by(id=user_id).first()
        user.email = email
        user.phone = phone
        user.updateAt = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 1})
    except:
        traceback.print_exc()
        return jsonify({'status': 0})

@app.route('/update-role-user', methods=['POST'])
@jwt_required
def update_role_user():
    """ update user """
    try:
        user_id = request.json.get('user_id')
        role = request.json.get('role')
        user = User.query.filter_by(id=user_id).first()
        user.role = role
        user.updateAt = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 1})
    except:
        traceback.print_exc()
        return jsonify({'status': 0})

@app.route('/new-user', methods=['POST'])
def new_user():
    """ add new user """
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        domain_active = request.json.get('domain_active')
        # Use scalar is appreciated
        checked_username = User.query.filter_by(
            username=username).scalar() is not None
        checked_email = User.query.filter_by(email=email).scalar() is not None

        if (checked_email or checked_username):
            return jsonify({'status': 0, 'message': 'Email or Username Existed! Please type new username or email'})

        user = User(username,User.hash_password(password),email,"guest",format(random.randint(0,99999999), '08d'))
        user.confirmed = False

        user.confirmed_on = datetime.now()

        if domain_active is not None:
            process.send_async_email.delay(domain_active, email, username)
        db.session.add(user)
        db.session.commit()
        return jsonify({'status': 1, 'message': 'sign up success', 'email': email})
    except:
        traceback.print_exc()
        return jsonify({'status': 0, 'message': 'sign up error'})


@app.route('/confirm-account', methods=['POST'])
def confirm_account():
    try:
        email_verify = request.json.get('email')
        token = request.json.get('token')
        print(email_verify)
        user = User.query.filter_by(email=email_verify).first()
        if(user.confirmed):
            return jsonify({
                'status': 1,
                'message': 'Account already confirmed. Please login'
            })
        if(common.checkBlacklist(blacklist_token, token)):
            return jsonify({
                'status': -1,
                'message': 'The confirmation link is invalid or has expired.'
            })
        try:
            email = process.confirm_token(token)
        except:
            blacklist_token.add(token)
            traceback.print_exc()
            return jsonify({
                'status': -1,
                'message': 'The confirmation link is invalid or has expired.'
            })
        if (not email):
            return jsonify({
                'status': -1,
                'message': 'The confirmation link is invalid or has expired.'
            })
        if (email_verify != email):
            return jsonify({
                'status': -1,
                'message': 'The confirmation link is invalid or has expired.'
            })
        user.role ="trader"
        user.confirmed = True
        user.confirmed_on = datetime.now()
        data_request = {
            'user_id': user.id,
            'currency': "BTC"
        }
        try:
            res_btc = requests.post(config.DEPOST_APP + '/account/open', json = data_request)
            data_request['currency']='ETH'
            res_eth = requests.post(config.DEPOST_APP + '/account/open', json = data_request)
            data_request['currency']='USDT'
            res_usdt = requests.post(config.DEPOST_APP + '/account/open', json = data_request)
            data_request['currency']='VND'
            res_vnd = requests.post(config.DEPOST_APP + '/account/open', json = data_request)
        except:
            traceback.print_exc()
            pass
        
        db.session.commit()
        return jsonify({
            'status': 1,
            'message': 'Account confirm Success. Please login'
        })
    except:
        traceback.print_exc()
        return jsonify({
            'status': 0,
            'message': 'Account confirm error. Please reconfirm account'
        })


@app.route('/resend-confirm', methods=['POST'])
def resend_confirm():
    try:
        email = request.json.get('email')
        domain_active = request.json.get('domain_active')
        user = User.query.filter_by(email=email).first()
        process.send_async_email.apply_async(
            args=[domain_active, email, user.username], countdown=10)
        return jsonify({
            'status': 'success',
            'message': 'Resend Email success'
        })
    except:
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'Resend Email error. Please resend email to active your account'
        })

@app.route('/role', methods=['POST'])
def new_role():
    """create new role"""
    try:
        role_name = request.json.get('role_name')
        description = request.json.get('description')
        return jsonify(process.add_new_role(role_name, description))
    except:
        traceback.print_exc()
        return jsonify({'status': 0, 'message': 'Invalid Role'})


@app.route('/update-role', methods=['POST'])
def update_role():
    """update role"""
    try:
        role_id = request.json.get('role_id')
        role_name = request.json.get('role_name')
        role_description = request.json.get('description')
        
        role = Role.query.filter_by(id=role_id).first()
        role.name = role_name
        role.description = role_description
        db.session.commit()
        return jsonify({'status': 1,
                        'message': 'update role success'})
    except:
        traceback.print_exc()
        return jsonify({'status': 0, 'message': 'Invalid Role'})


@app.route('/delete-role', methods=['POST'])
def delete_role():
    """delete role"""
    try:
        role_id = request.json.get('role_id')
        role = Role.query.filter_by(id=role_id)
        if (not role):
            return jsonify({
                'status': 0,
                'message': 'Role dont exited'
            })
        db.session.delete(role)
        db.session.commit()
        return jsonify({
            'status': 1,
            'message': 'Delete role success'
        })
    except:
        traceback.print_exc()
        return jsonify({
            'status': 0,
            'message': 'Delete role error'
        })


@app.route('/add-permission', methods=['POST'])
def add_premission():
    """add permission to role"""
    role_id = request.json.get('role_id')
    permission = request.json.get('permission')
    new_permission = Permission(role_id, permission)
    db.session.add(new_permission)
    db.session.commit()
    return jsonify({
        'status': 1,
        'message': 'Add permission success'
    })
    


@app.route('/delete-permission', methods=['POST'])
def remove_premission():
    """remove permission to role"""
    permision_query = request.json.get('permission')
    permission = Permission.query.filter_by(permission = permision_query)
    if (not permission):
        return jsonify({
            'status': 0,
            'message': 'Role dont exited'
        })
    db.session.delete(permission)
    db.session.commit()
    return jsonify({
        'status': 1,
        'message': 'Delete permission success'
    })
@app.route('/add-kyc', methods=['POST'])
def add_kyc():
    """add kyc to user"""
    try:
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        id_verify = request.form.get('id_verify')
        user_id = request.form.get('user_id')
        print(full_name)
        image_front = request.files['image_front_verify']
        image_selfie = request.files['image_selfie_verify']
        image_with = request.files['image_with_verify']
        image_alternative = request.files['image_alternative']
        print(image_front)
        dictory_user = os.path.join(config.FOLDER_KYC,user_id)
        if not os.path.exists(dictory_user):
            os.makedirs(dictory_user)

        user = User.query.filter_by(id = user_id).first()
        list_name = common.saveListImage([image_front,image_selfie,image_with,image_alternative],dictory_user,user.username)
        kyc = Kyc(full_name,phone,id_verify,list_name[0],list_name[1],list_name[2],list_name[3],user_id)
        db.session.add(kyc)
        db.session.commit()
        return jsonify({
            'status': 1,
            'message': 'Info user to verify success, Plese wait some minute to supporter verify info account '
        })
    except:
        traceback.print_exc()
        return jsonify({
                'status': 0,
                'message': 'Upload Info Kyc error'
            })

@app.route('/update-kyc', methods=['POST'])
def update_kyc():
    """update info kyc of user if verify fail"""
    try:
        id= request.form.get('id')
        print(id)
        kyc = Kyc.query.filter_by(id = id).first()
        user_id = kyc.user_id
        field_error = request.form.get('field_error')
        folder = os.path.join(config.FOLDER_KYC,str(user_id))
        user = User.query.filter_by(id = user_id).first()
        username = user.username
       
        status = request.form.get('status')
        kyc.status = status
        kyc.field_error = field_error
        print(request.files)
        if not os.path.exists(folder):
            os.makedirs(folder)
        if("full_name" in request.form):
            full_name = request.form.get('full_name')
            kyc.full_name = full_name
        if("phone" in request.form):
            phone = request.form.get('phone')
            kyc.phone = phone
        if("id_verify" in request.form):
            id_verify = request.form.get('id_verify')
            kyc.id_verify = id_verify
        if("image_front_verify" in request.files):
            image_front_verify = request.files["image_front_verify"]
            image_front_verify.save(os.path.join(folder,username+"_front.jpg"))
            kyc.image_front_verify = os.path.join(folder,username+"_front.jpg").replace("/AuthAPI/static","")
        if("image_selfie_verify" in request.files):
            image_selfie_verify = request.files["image_selfie_verify"]
            image_selfie_verify.save(os.path.join(folder,username+"_selfie.jpg"))
            kyc.image_selfie_verify = os.path.join(folder,username+"_selfie.jpg").replace("/AuthAPI/static","")
        if("image_with_verify" in request.files):
            image_with_verify = request.files["image_with_verify"]
            image_with_verify.save(os.path.join(folder,username+"_with_exchange.jpg"))
            kyc.image_with_verify = os.path.join(folder,username+"_with_exchange.jpg").replace("/AuthAPI/static","")
        if("img_alternative" in request.files):
            image_alternative = request.files["img_alternative"]
            image_alternative.save(os.path.join(folder,username+"_alternative.jpg"))
            kyc.image_alternative = os.path.join(folder,username+"_alternative.jpg").replace("/AuthAPI/static","")

        db.session.add(kyc)
        db.session.commit()
        return jsonify({
            'status': 1,
            'message': 'Update info kyc of user success'
        })
    except:
        traceback.print_exc()
        return jsonify({
            'status': 0,
            'message': 'Error System'
        })
    
@app.route('/checked-kyc', methods=['POST'])
def checked_kyc():
    """remove permission to role"""
    user_id = request.json.get('user_id')
    kyc = Kyc.query.filter_by(user_id = user_id).first()
    print(kyc)
    if(kyc is None):
        return jsonify({
            'status': -1
        })
    if(kyc.status != 1):
        return jsonify({
            'status': kyc.status,
            'message': 'kyc error',
            "file_error": kyc.field_error,
            "id": kyc.id
        }) 
    else: 
        return jsonify({
            'status': kyc.status,
            'message': 'kyc success',
            "file_error": "",
            "id": kyc.id
        })
@app.route('/kyc-pending', methods=['POST'])
def kyc_pending():
    """remove permission to role"""
    try:
        kyc = Kyc.query.filter_by(status = 0).all()
        print(kyc)
        if(kyc is None):
            return jsonify({
                'status': -1
            })
        data = [common.getFullAttr(item) for item in kyc]
        print(data)
        return jsonify({
            'status': 1,
            'kyc' : data
            
        })
    except:
        traceback.print_exc()
        return jsonify({
                'status': -1
            })
     
   