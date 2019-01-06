from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime

class Artist(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    aboutMe=db.Column(db.String(300))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('group.id'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupName= db.Column(db.String(140))
    groupDescription = db.Column(db.String(140))
    artists = db.relationship('Artist', backref='group', lazy='dynamic')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    return Artist.query.get(int(id))
