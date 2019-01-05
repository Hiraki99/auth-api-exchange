from flask import Flask, request, redirect, jsonify, send_from_directory, render_template, session
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timedelta
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from flask_jwt_extended import JWTManager
from celery import Celery
from flask_mail import Mail, Message
import AuthAPI.common as common
import AuthAPI.config as config
import sys,traceback
from itsdangerous import URLSafeTimedSerializer
import uuid, random
import redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=2)



public_key = common.get_key('./key/mykey.pub')
private_key = common.get_key('./key/mykey.pem')
expires = timedelta(seconds=604800)

app = Flask(__name__)
app.config["MAX_FILE_SIZE"] = 5000000  # 5MB
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
app.config['JWT_PUBLIC_KEY'] = public_key
app.config['JWT_PRIVATE_KEY'] = private_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = expires
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # enable will add significant overhead
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['JWT_ALGORITHM'] = 'RS256'
# Flask-Mail configuration
app.config['MAIL_SERVER'] = config.MAIL_SERVER
app.config['MAIL_PORT'] = config.MAIL_PORT
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_DEFAULT_SENDER
# connect_db
db = SQLAlchemy()
db.init_app(app)

# Initialize models
# from .model.user import User
# from .model.role import Role
# from .model.permission import Permission
from .model.kyc import Kyc

jwt = JWTManager(app)
# Celery configuration
app.config['CELERY_BROKER_URL'] = config.CELERY_BROKER_URL
app.config['result_backend'] = config.result_backend

# Initialize extensions
mail = Mail(app)

# Initialize Celery
celery = Celery(app.name, backend=app.config['result_backend'], broker = app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

blacklist = set()
blacklist_token = list()
serializer = URLSafeTimedSerializer(config.SECRET_KEY) # where this object come from ?


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

from .controller.views import *
from .crontab import crontab



def main():
    app.run(host='0.0.0.0', port=8001, debug=False)

if __name__ == "__main__":
    main()
