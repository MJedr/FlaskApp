from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from flask_login import UserMixin
from hashlib import md5
from datetime import datetime


# class Member(db.Model):
#     member_id = db.Column(db.Integer, db.ForeignKey('artist.id'),
#                             primary_key=True)
#     group_id = db.Column(db.Integer, db.ForeignKey('group.id'),
#                             primary_key=True)

#association table
members=db.Table('members',
                 db.Column('artist_id', db.Integer, db.ForeignKey('artist.id')),
                db.Column('group_id', db.Integer, db.ForeignKey('group.id')))

class Artist(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    aboutMe=db.Column(db.String(300))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    groups = db.relationship(
        'Group',
        secondary=members,
        backref=db.backref('members', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def is_in(self, group):
        return self.groups.filter(
            members.c.artist_id == group.id).count() > 0

    def join_group(self, group):
        if not self.is_in(group):
            self.groups.append(group)

    def quit(self, group):
        if self.is_following(group):
            self.groups.remove(group)

    def followed_posts(self):
        return Post.query.join(
            members, (members.c.group_id == Post.user_id)).order_by(
            Post.timestamp.desc())

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupName= db.Column(db.String(140))
    groupDescription = db.Column(db.String(140))
    event=db.relationship('Event', backref='eventAuthor', lazy='dynamic')
    posts=db.relationship('Post', backref='postAuthor', lazy='dynamic')

    def create_event(self, name, location, description, date):
        e = Event(eventName=name, location=location, eventDescription=description,
                  date=date, group=self.id)
        return e


    def __repr__(self):
        return '<Post {}>'.format(self.groupName)

class Event(db.Model):
    __tablename__='events'

    id = db.Column(db.Integer, primary_key=True)
    eventName = db.Column(db.String(60), unique=True, nullable=False)
    location = db.Column(db.String(100))
    eventDescription = db.Column(db.String(100))
    isFree = db.Column(db.Boolean)
    date = db.Column(db.DateTime)
    event_author = db.Column(
        db.Integer, db.ForeignKey('group.id'), nullable=True
    )

    def __repr__(self):
        return '<Event: {}'.format(self.eventName)


class Post(db.Model):
    __tablename__='posts'

    id=db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_author = db.Column(
        db.Integer, db.ForeignKey('group.id'), nullable=True
    )

@login.user_loader
def load_user(id):
    return Artist.query.get(int(id))
