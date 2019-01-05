from sqlalchemy.orm import backref
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupName= db.Column(db.String(140))
    groupDescription = db.Column(db.String(140))
    artists = db.relationship('Artist', backref='group', lazy='dynamic')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

