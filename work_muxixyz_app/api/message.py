from flask import jsonify, request, current_app, url_for
from functools import cmp_to_key
from . import api
from .. import db
from ..models import Team, Group, User, Project, User2Project, Message, Statu, File, Comment, User2File, Doc
from ..decorator import login_required
from ..timetools import to_readable_time
from operator import lt
import time

@api.route('/user/attention/',methods = ['POST', 'GET', 'DELETE'],endpoint = 'UserAttention')
@login_required(role = 1)
def user_attention(uid):
    if request.method  ==  'POST':
        fileID = request.get_json().get('fileID')
        f = File.query.filter_by(id = fileID).first()
        if f is None:
            response = jsonify({})
            response.status_code = 402
            return response
        rela = User2File(user_id = uid,file_id = fileID)
        db.session.add(rela)
        db.session.commit()
        response = jsonify({})
        response.status_code = 200
        return response
    if request.method  ==  'GET':
        l = list([])
        files = User2File.query.filter_by(user_id = uid).all()
        for f_id in files:
            f = File.query.filter_by(id = f_id.file_id).first()
            editor = User.query.filter_by(id = f.editor_id).first()
            if editor is None:
                editor = User.query.filter_by(id = f.creator_id).first()
            project = Project.query.filter_by(id = f.project_id).first()
            l.append({
                "fileName": f.filename,
                "userName": editor.name,
                "projectName": project.name,
                "date": f.time,
            })
        response = jsonify({
            "list": l,
        })
        response.status_code = 200
        return response
    if request.method == 'DELETE':
        fileName = request.args.get('fileName')
        f = File.query.filter_by(filename = fileName).first()
        if f is None:
            response = jsonify({
                "fileName": fileName,
            })
            response.status_code = 403
            return response
        record = User2File.query.filter_by(file_id = f.id).first()
        db.session.delete(record)
        db.session.commit()
        response = jsonify({})
        response.status_code = 200
        return response

@api.route('/message/new/',methods = ['POST'],endpoint = 'MessageNew')
@login_required(role = 1)
def message_new(uid):
    receiver = request.get_json().get('receiver')
    maker = request.get_json().get('maker')
    action = request.get_json().get('action')
    sourceID = request.get_json().get('sourceID')
    Mer = User.query.filter_by(name = maker).first()
    Rer = User.query.filter_by(name = receiver).first()
    if uid !=  Rer.id:
        response = jsonify({})
        response.status_code = 401
        return response
    msg = Message(
        time = to_readable_time(time.time()),
        action = action,from_id = Mer.id,receive_id = Rer.id,file_id = sourceID)
    db.session.add(msg)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

@api.route('/message/list/',methods = ['GET'],endpoint = 'MessageList')
@login_required(role = 1)
def message_list(uid):
    kind = request.args.get('kind')
    msgs = Message.query.filter_by(receive_id = uid,readed = False).order_by(Message.id).all()
    l = list([])
    limit = 0
    if kind  ==  1: #hover
        limit = 5
    if kind  ==  0: #click
        limit = None
    c = 1
    for m in msgs:
        usr = User.query.filter_by(id = m.from_id).first()
        if usr is None:
            response = jsonify({
                "msg": 'user is gone.',
            })
            response.status_code = 401
            return response
        l.append({
            "sourceID": m.file_id,
            "fromName": usr.name,
            "fromAvatar": usr.avatar,
            "time": m.time,
            "readed": m.readed,
        })
        c += 1
        if limit is None:
            continue
        if c  ==  limit+1:
            break
    response = jsonify({
        "list": l,
    })
    response.status_code = 200
    return response

@api.route('/message/readAll/',methods = ['POST'],endpoint = 'ReadAll')
@login_required(role = 1)
def read_all(uid):
    username = request.get_json().get('username')
    usr = User.query.filter_by(name = username).first()
    if uid !=  usr.id:
        response = jsonify({})
        response.status_code = 401
        return response
    unread = Message.query.filter_by(receive_id = uid,readed = False).all()
    for m in unread:
        m.readed = True
        db.session.add(m)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

@api.route('/message/<string:username>/<int:mid>/',methods = ['GET'],endpoint = 'MessageInfo')
@login_required(role = 1)
def message_info(uid,username,mid):
    usr = User.query.filter_by(name = username).first()
    if (usr is None) or (usr.id !=  uid):
        response = jsonify({})
        response.status_code = 402
        return response
    msg = Message.query.filter_by(id = mid).first()
    if msg is None:
        response = jsonify({
            "msg": 'message is None'
        })
        response.status_code = 403
        return response
    usr = User.query.filter_by(id = msg.from_id).first()
    response = jsonify({
        "msgID": mid,
        "fromName": usr.name,
        "time": msg.time,
        "action": msg.action,
        "sourceID": msg.file_id,
    })
    response.status_code = 200
    return response
