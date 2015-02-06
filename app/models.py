from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True)
    password = db.Column(db.String(64))
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
    
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        self.set_password(password)
        return check_password_hash(self.pw_hash, password)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)    


channels_users = db.Table('channels_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('channel_id', db.Integer, db.ForeignKey('channel.id'))
)


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    users = db.relationship('User', secondary=channels_users, backref=db.backref('channels'), lazy='dynamic')
    posts = db.relationship('Post', backref = 'channel', lazy = 'dynamic')
    
    def remove_user(self, user):
        db.engine.execute("delete from channels_users where channel_id=%d and user_id=%d" % (self.id, user.id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    
    def __repr__(self):
        return '<Post %r>' % (self.body)
