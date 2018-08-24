from functools import wraps
from flask import abort,request
from flask import current_app
# import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .models import User

def middle(self):
    pass

def login_required(role):
    def deco(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not 'token' in request.headers:
                print (request.headers)
                abort(401)
            t=request.headers['token'].encode('utf-8')
            s=Serializer(current_app.config['SECRET_KEY'])
            try:
                data=s.loads(t)
            except:
                abort(401)
            uid=data.get('confirm')
            usr=User.query.filter_by(id=uid).first()
            if role&usr.role != role:
                abort(401)
            rv=f(uid,*args,**kwargs)
            return rv
#        middle.__name__=f.__name__
        return decorated_function
    return deco
