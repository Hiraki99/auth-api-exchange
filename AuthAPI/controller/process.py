from AuthAPI import app, db, celery, config, common
from AuthAPI import jwt, blacklist, blacklist_token, mail, serializer
import traceback
from flask_mail import Mail, Message
# Initialize models
from AuthAPI.model.user import User
from AuthAPI.model.role import Role
from AuthAPI.model.permission import Permission
from jinja2 import Template

HTML = """
    <div id=":mb" class="a3s aXjCH m1643d0b2a770ec0a">
        <p><span style="font-size:12px;margin-bottom:40px">Dear <strong>{{username}}</strong>,</span></p>
        <p><span style="font-size:12px">Welcome to the world of decentralized anonymous ai blockchain.</span></p>
        <p><span style="font-size:12px">In order to activate your account and start the next generation crypto-currency, please follow this activation link.</span></p>
        <p style="margin:20px 0px">
            <span style="font-size:12px">
                <a href="{{link_confirm}}" style="font-family:Helvetica,Arial,sans-serif;font-size:24px;text-decoration:none;color:rgb(255,255,255);padding:12px 35px;border-radius:4px;border:1px solid rgb(23,144,218);background:rgb(0,175,236)" rel="noreferrer" target="_blank">Activate ›</a>
            </span>
        </p>
        <p><span style="font-size:12px">In order to access your account please go to: <a href="{{link_login}}" target="_blank">{{link_login}}
            </a></span>
        </p>
        <p><span style="font-size:12px">We thank you for choosing T-Rex and wish you successful at T-Rex.</span></p>
        <p><span style="font-size:12px">If you have any questions or concerns, you can email us at: <a href="mailto:support@t_rex.co" target="_blank">support@t_rex.co</a> or visit our Contact Us page.</span></p>
        <br>
        <p><span style="font-size:12px;margin-bottom:40px">Regards, </span></p>
        <p><strong><span style="font-size:12px">T-Rex Support Team!</span></strong></p>
    </div>
"""

def generate_confirmation_token(email):
    return serializer.dumps(email, salt=config.SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=86400):
    try:
        email = serializer.loads(
            token,
            salt=config.SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except:
        traceback.print_exc()
        return False
    return email


@celery.task
def send_async_email(host_url, recipients, username):
    # """Background task to send an email with Flask-Mail."""

    try:
        with app.app_context():

            list_mail = list()
            list_mail.append(recipients)
            token = generate_confirmation_token(recipients)
            link_confirm = host_url + '/confirmaccount/' + recipients+'/' + token
            link_login = host_url + '/login'
            template = Template(HTML)
            body = template.render(username = username, link_login = link_login, link_confirm = link_confirm)
            msg = Message('Welcome to T-Rex Exchange Cryptocurrency',
                          recipients=list_mail, html=body, sender=config.MAIL_DEFAULT_SENDER,)

            mail.send(msg)

    except:
        traceback.print_exc()


def add_new_role(role_name, description):
    new_role:Role = Role.query.filter_by(name=role_name).first()

    if new_role is not None:
        return {'status': 0, 'message': 'role already existed'}
    
    new_role=Role(role_name, description)

    db.session.add(new_role)
    db.session.commit()
    return {'status': 1, 'message': 'add new role success'}
