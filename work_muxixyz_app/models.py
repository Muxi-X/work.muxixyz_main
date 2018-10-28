import time
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(35), unique=True)
    avatar = db.Column(db.Text, default="default")
    tel = db.Column(db.String(15))
    role = db.Column(db.Integer, default=0)
    email_service = db.Column(db.Boolean, default = False)
    message = db.Column(db.Boolean, default = False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    status = db.relationship('Statu', backref='user', lazy='dynamic')
    receiveMsgs = db.relationship('Message', backref='user', lazy='dynamic')
    
    def generate_confirmation_token(self, expiration=360000000):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id}).decode('utf-8')

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)
    count = db.Column(db.Integer)
    time = db.Column(db.String(50))
    creator = db.Column(db.Integer)
    users = db.relationship('User', backref='team', lazy='dynamic')

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True)
    order = db.Column(db.Integer, unique=True, default=None)
    count = db.Column(db.Integer)
    leader = db.Column(db.Integer)
    time = db.Column(db.String(30))
    users = db.relationship('User', backref='group', lazy='dynamic')

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    intro = db.Column(db.String(100))
    time = db.Column(db.String(50))
    count = db.Column(db.Integer, default=0)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    filetree = db.Column(db.Text, default='')
    doctree = db.Column(db.Text, default='')

class Apply(db.Model):
    __tablename__ = 'applys'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class User2Project(db.Model):
    __tablename__ = 'user2projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    project_id = db.Column(db.Integer)


class Statu(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    title = db.Column(db.String(20))
    time = db.Column(db.String(50))
    like = db.Column(db.Integer)
    comment = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments=db.relationship('Comment', backref='statu', passive_deletes=True, cascade='delete',lazy='dynamic')


class FolderForFile(db.Model):
    __tablename__ = 'foldersforfiles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    create_time = db.Column(db.String(30))
    create_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    re = db.Column(db.Boolean, default=False)


class FolderForMd(db.Model):
    __tablename__ = 'foldersformds'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    create_time = db.Column(db.String(30))
    create_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    re = db.Column(db.Boolean, default=False)


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(150))
    filename = db.Column(db.String(150))
    realname = db.Column(db.String(150))
    re = db.Column(db.Boolean, default=False)
    top = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.String(30))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    comments = db.relationship('Comment', backref='file', passive_deletes=True, cascade='delete', lazy='dynamic')


class Doc(db.Model):
    __tablename__ = 'docs'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150))
    content = db.Column(db.Text)
    re = db.Column(db.Boolean, default=False)
    top = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.String(30))
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    comments = db.relationship('Comment', backref='doc', passive_deletes=True, cascade='delete', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.Integer)
    content = db.Column(db.Text)
    time = db.Column(db.String(50))
    creator = db.Column(db.Integer)
    doc_id = db.Column(db.Integer, db.ForeignKey('docs.id', ondelete='cascade'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id', ondelete='cascade'))
    statu_id = db.Column(db.Integer, db.ForeignKey('status.id', ondelete='cascade'))

    
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(30))
    action = db.Column(db.Text)
    readed = db.Column(db.Boolean, default=False)
    from_id = db.Column(db.Integer)
    receive_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_kind = db.Column(db.Integer)
    file_id = db.Column(db.Integer)
   

class Feed(db.Model):
    __tablename__ = 'feeds'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    username = db.Column(db.String(100))
    useravatar = db.Column(db.String(200))
    action = db.Column(db.String(20))
    source_kindid = db.Column(db.Integer)
    source_objectname = db.Column(db.String(100))
    source_objectid = db.Column(db.Integer)
    source_projectname = db.Column(db.String(100))
    source_projectid = db.Column(db.Integer)
    timeday = db.Column(db.String(20))
    timehm = db.Column(db.String(20))



class User2File(db.Model):
    __tablename__ = 'user2files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    file_id = db.Column(db.Integer)
    file_kind = db.Column(db.Integer, default = 0)
