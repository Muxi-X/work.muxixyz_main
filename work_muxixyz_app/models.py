import time
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique = True)
    email = db.Column(db.String(35), unique = True)
    avatar = db.Column(db.String(50))
    tel = db.Column(db.String(15))
    role = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    status = db.relationship('Statu', backref='user', lazy='dynamic')
    receiveMsgs = db.relationship('Message', backref='user', lazy='dynamic')
    # efiles = db.relationship('File', backref='user', lazy='dynamic')
    # cfiles = db.relationship('File', backref='user', lazy='dynamic')

    @staticmethod
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirm = True
        db.session.add(self)
        return True


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique = True)
    count = db.Column(db.Integer)
    time = db.Column(db.String(50))
    creator = db.Column(db.Integer)
    users = db.relationship('User', backref='team', lazy='dynamic')

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique = True)
    count = db.Column(db.Integer)
    leader = db.Column(db.Integer)
    time = db.Column(db.String(30))
    users = db.relationship('User',backref='group',lazy='dynamic')

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique = True)
    intro = db.Column(db.String(100))
    time = db.Column(db.String(50))
    count = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    files = db.relationship('File', backref='project', lazy='dynamic')
    folders = db.relationship('Folder', backref='project', lazy='dynamic')


class User2Project(db.Model):
    __tablename__ = 'user2projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    project_id = db.Column(db.Integer)


class Statu(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    time = db.Column(db.String(50))
    like = db.Column(db.Integer)
    comment = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='statu', lazy='dynamic')


class Folder(db.Model):
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    father_id = db.Column(db.Integer, db.ForeignKey('folders.id'))
    # father = db.relationship('Folder', backref=db.backref('children'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    # project = db.relationship('Project', backref=db.backref('folders'))
    files = db.relationship('File', backref='folder', lazy='dynamic')


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(150), unique = True)
    filename = db.Column(db.String(150))
    kind = db.Column(db.Boolean, default=False)
    editor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # editor = db.relationship('User', backref=db.backref('efiles'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # creator = db.relationship('User', backref=db.backref('cfiles'))
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'))
    # folder = db.relationship('Folder', backref=db.backref('ffiles'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    # project = db.relationship(Project, backref=db.backref('pfiles'))
    # comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    # comment = db.relationship('Comment', backref=db.backref('comments'))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    kind = db.Column(db.Integer)
    content = db.Column(db.Text)
    time = db.Column(db.String(50))
    creator = db.Column(db.Integer)
    fileID = db.Column(db.Integer, db.ForeignKey('files.id'), default=0)
    file = db.relationship('File', backref=db.backref('comments'))
    statuID = db.Column(db.Integer, db.ForeignKey('status.id'), default=0)


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(30))
    action = db.Column(db.Text)
#    kind = db.Column(db.Integer)
    readed = db.Column(db.Boolean, default=False)
    from_id = db.Column(db.Integer)
    receive_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), default=0)
#    statu_id = db.Column(db.Integer, db.ForeignKey('status.id'), default=0)
#    commen_id = db.Column(db.Integer, db.ForeignKey('comments.id'), default=0)

class User2File(db.Model):
    __tablename__ = 'user2files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    file_id = db.Column(db.Integer)

def init_db():
    db.create_all()
    usr = User(name='tst', email='tst@test.com', tel='11111111111')
    db.session.add(usr)
    db.session.commit()


if __name__ == '__main__':
#    init_db()
    db.create_all()
