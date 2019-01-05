import sys
import os
from datetime import datetime
from AuthAPI import db
from passlib.apps import custom_app_context as pwd_context
import hashlib


class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    passwordresettoken = db.Column(db.String(250),default='')
    passwordresetexpires = db.Column(db.DateTime,default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_on = db.Column(db.DateTime)
    email = db.Column(db.String(250), unique=True, nullable=False)
    phone = db.Column(db.String(30), unique=True, nullable=False,default='')
    facebook = db.Column(db.String(250),default='')
    google = db.Column(db.String(250),default='')
    linkin = db.Column(db.String(250),default='')

    live = db.Column(db.Boolean, default=True, nullable=False)
    createAt = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    updateAt = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    
    role = db.Column(db.String(125), nullable=False)

    def __init__(self, username, password, email,role,phone):
        """[Create New User for T-Rex]
        
        Arguments:
            username {[string]} -- [user name user login]
            password {[type]} -- [Password for user login]
            email {[type]} -- [Email regist t-rex exchange]
            role {[type]} -- [Role of user]
        """
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.phone = phone

    def __repr__(self):
        return '<User %r>' % self.username
    
    @staticmethod
    def hash_password(password):
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)


