from functools import wraps
from flask import abort,request
from flask import current_app, jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .models import User

def middle(self):
    pass

def login_required(role):
    def deco(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not 'token' in request.headers:
                return jsonify({}), 401
            t = request.headers['token'].encode('utf-8')
            s = Serializer(current_app.config['SECRET_KEY'])
            try:
                data = s.loads(t)
            except:
                return jsonify({}), 401
            uid = data.get('confirm')
            usr = User.query.filter_by(id=uid).first()
            if role&usr.role != role:
                return jsonify({}), 401
            rv = f(uid,*args,**kwargs)
            return rv
        return decorated_function
    return deco

class login_re(object):
    def __init__(self, role=1):
        self.role = role

    def __call__(self, func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not 'token' in request.headers:
                return jsonify({}),401
            t=request.headers['token'].encode('utf-8')
            s=Serializer(current_app.config['SECRET_KEY'])
            try:
                data=s.loads(t)
            except:
                return jsonify({}), 401
            uid=data.get('confirm')
            usr=User.query.filter_by(id=uid).first()
            if self.role&usr.role != role:
                return jsonify({}), 401
            rv=func(uid, *args, **kwargs)
            return rv
        return decorated_function
