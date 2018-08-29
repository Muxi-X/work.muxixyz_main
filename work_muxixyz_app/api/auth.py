from flask import jsonify,request,current_app,url_for
from . import api
from .. import db
from ..models import Team,Group,User,Project,Message,Statu,File,Comment
from ..decorator import login_required

from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@api.route('/auth/login/',methods=['POST'])
def login():
    usrname=request.get_json().get('username')
    usr=User.query.filter_by(name=usrname).first()
    if usr is None:
        response=jsonify({
            "msg": 'user not existed!',
        })
        response.status_code=401
        return response
    else:
        token=usr.generate_confirmation_token(usr)
        response=jsonify({
            "token": token,
        })
        response.status_code=200
        return response