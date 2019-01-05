import sys
import os
from datetime import datetime
from AuthAPI import db


class Kyc(db.Model):
    __tablename__ = 'KYC'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(125), nullable=False, default= "")
    phone = db.Column(db.String(125), nullable=False, default= "")
    id_verify = db.Column(db.String(125), nullable=False, default= "")
    image_front_verify = db.Column(db.String(125), nullable=False, default= "")
    image_selfie_verify = db.Column(db.String(125), nullable=False, default= "")
    image_with_verify = db.Column(db.String(125), nullable=False, default= "")
    image_alternative = db.Column(db.String(125), nullable=False, default= "")
    createAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updateAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    field_error = db.Column(db.String(125), default= "")
    #0 : pending , 1: success, 2 : fail
    status =  db.Column(db.Integer, nullable=False, default= 0)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'),unique=True)

    def __init__(self, full_name, phone,id_verify,image_front_verify,image_selfie_verify,image_with_verify,image_alternative,user_id):
        self.full_name = full_name
        self.phone = phone
        self.id_verify = id_verify
        self.image_front_verify = image_front_verify
        self.image_with_verify = image_with_verify
        self.image_selfie_verify = image_selfie_verify
        self.image_alternative = image_alternative
        self.user_id = user_id
    def __repr__(self):
        return '<KYC %r>' % self.full_name

    # @staticmethod
    # def get_permission_by_role(role_name):
    #     """"""
    #     role = Role.query.filter_by(name=role_name).first()
    #     list_permit = [row.permission for row in role.permission]
    #     return list_permit
