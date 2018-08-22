from functools import wraps
from flask import abort,request
from flask import current_app
# import jwt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
            if not 'token' in request.headers:
                print (request.headers)
                abort(401)
            usr=None
            t=request.headers['token'].encode('utf-8')
            s=Serializer(current_app.config['SECRET_KEY'])
#            print (s.loads(t))
            try:
                data=s.loads(t)
            except:
                abort(401)
            uid=data.get('confirm')
#            if uid is None:
#                print ('you write a shit decorator!')
#            print (t,s)
            return f(uid,*args,**kwargs)
    return decorated_function
