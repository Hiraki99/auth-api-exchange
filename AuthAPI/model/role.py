import sys
import os
from datetime import datetime
from AuthAPI import db


class Role(db.Model):
    __tablename__ = 'Role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(125), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    createAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updateAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    permission = db.relationship('Permission', backref='Role', lazy='dynamic')

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.updateAt = datetime.utcnow()

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def get_permission_by_role(role_name):
        """"""
        role = Role.query.filter_by(name=role_name).first()
        list_permit = [row.permission for row in role.permission]
        return list_permit
