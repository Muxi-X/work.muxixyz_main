# -*- coding: UTF-8 -*-
from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Team, Group, User, Project, User2Project, Message, Statu, File, Comment, Apply, Doc
from ..decorator import login_required
from ..timetools import to_readable_time
from ..page import get_rows
from ..mq import newfeed
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
import time
import os
from werkzeug import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

access_key = os.environ.get('WORKBENCH_ACCESS_KEY')
secret_key = os.environ.get('WORKBENCH_SECRET_KEY')
url = os.environ.get('WORKBENCH_URL')
bucket_name = 'ossworkbench'
q = qiniu.Auth(access_key, secret_key)
bucket = BucketManager(q)


def qiniu_upload(key, localfile):
    token = q.upload_token(bucket_name, key, 3600)

    ret, info = qiniu.put_file(token, key, localfile)

    if ret:
        return '{0}{1}'.format(url, ret['key'])
    else:
        raise UploadError('上传失败，请重试')

#role: 000
@api.route('/user/2bSuperuser/', methods = ['POST'], endpoint = '2BSuperUser')
def user_2b_super_user():
    username = request.get_json().get("name")
    usr = User.query.filter_by(name = username).first()
    usr.role = 7
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 100
@api.route('/group/new/', methods = ['POST'], endpoint = 'NewGroup')
@login_required(role = 4)
def new_group(uid):
    gname = request.get_json().get('groupName')
    ulist = request.get_json().get('userlist')
    if Group.query.filter_by(name=gname).first() is not None:
        return jsonify({"msg": "group name exist!"}), 402
    if ulist is None:
        return jsonify({"msg": "user list is None!"}), 402
    group = Group(
        time = to_readable_time(str(int(time.time()))),
        name = gname, 
        count = 0
    )
    for u in ulist:
        usr = User.query.filter_by(id = u).first()
        if usr is None:
            continue
        group.count += 1
        usr.group_id = group.id
        db.session.add(usr)
    db.session.add(group)
    db.session.commit()
    response = jsonify({
        "msg": 'successful!', 
    }), 200
    return response

#role: 010
@api.route('/group/<int:gid>/', methods = ['DELETE'], endpoint = 'GroupDelete')
@login_required(role = 2)
def group_delete(uid, gid):
    grp = Group.query.filter_by(id = gid).first()
    for u in grp.users:
        u.group_id = None
        db.session.add(u)
    db.session.delete(grp)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

@api.route('/group/<int:gid>/rename/', methods = ['POST'], endpoint = "GroupRename")
@login_required(role = 2)
def group_rename(uid, gid):
    rename = request.get_json().get("rename")
    if rename == "" or rename is None:
        return jsonify({"msg": "rename is None"}), 402
    grp = Group.query.filter_by(id = gid).first()
    grp.name = rename
    db.session.add(grp)
    try:
        db.session.commit()
    except:
        return jsonify({"msg": "please keep group name unique!"}), 402
    return jsonify({"msg": "rename successful!"}), 200

#role: 001
@api.route('/group/<int:gid>/userList/', methods = ['GET'], endpoint = 'GroupUserList')
@login_required(role = 1)
def group_user_list(uid, gid):
    role = 1
    if gid  ==  0 :
        data = User.query.filter_by(team_id = 1).all()
    else:
        data = User.query.filter_by(group_id = gid).all()
        grp = Group.query.filter_by(id = gid).first()
        groupName = grp.name
    l = list([])
    for u in data:
        if gid == 0:
            grp = Group.query.filter_by(id = u.group_id).first()
            if grp is None:
                groupName = 'NoneGroup'
            else:
                groupName = grp.name
        l.append({
            'teamID': u.team_id,
            'username': u.name,
            'userID': u.id,
            'groupName': groupName,
            'groupID': u.group_id,
            'role': u.role,
            'email': u.email,
            'avatar': u.avatar
        })
    userCount = len(l)
    if gid != 0:
        grp = Group.query.filter_by(id = gid).first()
        grp.count = userCount
        db.session.add(grp)
        db.session.commit()

    response = jsonify({
                 "count": len(l),
                 "list": l,
             })
    response.status_code = 200
    return response

#role: 110
@api.route('/group/<int:gid>/manageUser/', methods = ['POST'], endpoint = 'GroupManageUser')
@login_required(role = 2)
def group_manage_user(uid, gid):
    count_change = 0

    newUList = request.get_json().get('userList')
    oldUList = Group.query.filter_by(id = gid).first().users
    for u in newUList:
        usr = User.query.filter_by(id = u).first()
        if usr not in oldUList:
            usr.group_id = gid
            db.session.add(usr)
            count_change += 1
    for usr in oldUList:
        if usr.id not in newUList:
            usr.group_id=None
            db.session.add(usr)
            count_change -= 1
    grp = Group.query.filter_by(id = gid).first()
    grp.count += count_change
    if grp.count < 0:
        grp.count = 0
    db.session.add(grp)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 001
@api.route('/group/list/', methods = ['GET'], endpoint = 'GroupList')
@login_required(role = 1)
def group_list(uid):
    grps = db.session.query(Group).all()
    l = list([])
    for grp in grps:
        l.append({
            "groupID": grp.id,
            "groupName": grp.name,
            "userCount": grp.count,
        })
    response = jsonify({
        "groupList": l,
    })
    response.status_code = 200
    return response

#role: 001
@api.route('/project/<int:pid>/userList/', methods = ['GET'], endpoint = 'ProjectUserList')
@login_required(role = 1)
def project_user_list(uid, pid):
    data = User2Project.query.filter_by(project_id = pid).all()
    l = list([])
    for record in data:
        uid = record.user_id
        usr = User.query.filter_by(id = uid).first()
        l.append({
            "username": usr.name,
            "userID": uid,
            "avatar": usr.avatar,
        })
    pjc = Project.query.filter_by(id = pid).first()
    pjc.count = len(l)
    db.session.add(pjc)
    db.session.commit()
    response = jsonify({
                 "count": len(l),
                 "list": l,
             })
    response.status_code = 200
    return response

#role: 001
@api.route('/user/<int:id>/project/list/', methods = ['GET'], endpoint = 'UserProjectList')
@login_required(role = 1)
def user_project_list(uid, id):
    if uid != id:
        request_user = User.query.filter_by(id = uid).first()
        got_user = User.query.filter_by(id = id).first()
        if request_user.role < got_user.role:
            response = jsonify({
                "msg": 'you should get yourself information!',
            })
            response.status_code = 402
            return response
    page = 1
    pageSize = 10
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    usr = User.query.filter_by(id = id).first()
    l = list([])
    if usr.role >  1:
        data = get_rows(Project, None, None, page, pageSize)
        pjcs = data['dataList']
        for pjc in pjcs:
            l.append({
                "projectID": pjc.id,
                "projectName": pjc.name,
                "intro": pjc.intro,
                "userCount": data['rowsNum'],
            })
    else:
        data = get_rows(User2Project, User2Project.user_id, id, page, pageSize)
        records = data['dataList']
        for record in records:
            pid = record.project_id
            pjc = Project.query.filter_by(id = pid).first()
            l.append({
                "projectID": pjc.id,
                "projectName": pjc.name,
                "intro": pjc.intro,
                "userCount": data['rowsNum'],
            })
            if pjc.count != data['rowsNum']:
                pjc.count = data['rowsNum']
                db.session.add(pjc)
    db.session.commit()
    response = jsonify({
        "count": data['rowsNum'],
        "pageMax": data['pageMax'],
        "pageNow": data['pageNum'],
        "hasNext": data['hasNext'],
        "list": l,
    })
    response.status_code = 200
    return response

#role: 110
@api.route('/user/2bMember/', methods = ['POST'], endpoint = 'User2bMember')
@login_required(role = 2)
def user_2b_member(uid):
    actions = ["加入", "创建", "编辑", "删除", "评论", "移动"]
    sourceidmap = {
            "团队": 1,
            "项目": 2,
            "文档": 3,
            "文件": 4,
            "文件夹": 5,
            "进度": 6
        }
    user_id = request.get_json().get('userID')
    usr = User.query.filter_by(id = user_id).first()
    if (usr.role !=  0) and (usr.team_id is not None):
        response = jsonify({
            "msg": 'user already be a member!', 
        })
        response.status_code = 402
        return response
    if usr.role == 0:
        usr.role = 1
    usr.team_id = 1
    team = Team.query.filter_by(id=usr.team_id).first()
    db.session.add(usr)
    db.session.commit()
    newfeed(user_id, actions[0], team.name, sourceidmap["团队"], team.id)
    response = jsonify({
        "msg": 'successful!',
    })
    print ("4")
    response.status_code = 200
    return response

# role: 100
@api.route('/user/admins/', methods = ['GET'], endpoint = 'AdminList')
@login_required(role = 4)
def admin_list(uid):
    admins = db.session.query(User).all()
    if admins is None:
        response = jsonify({})
        response.status_code = 201
        return response
    l=list([])
    for admin in admins:
        if admin.role > 1:
            l.append({
                "userID": admin.id,
                "userName": admin.name,
            })
    response = jsonify({
        "list": l,
    })
    response.status_code = 200
    return response

#role: 100
@api.route('/user/addAdmin/', methods = ['POST'], endpoint = 'AddAdmin')
@login_required(role = 4)
def add_admin(uid):
    lid = request.get_json().get('luckydog')
    luckydog = User.query.filter_by(id = lid).first()
    luckydog.role = 3
    db.session.add(luckydog)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 100
@api.route('/user/delAdmin/', methods = ['POST'], endpoint = 'DeleteAdmin')
@login_required(role = 4)
def del_admin(uid):
    lid = request.get_json().get('unluckydog')
    unluckydog = User.query.filter_by(id = lid).first()
    unluckydog.role = 1
    db.session.add(unluckydog)
    db.session.commit()
    response = jsonify({"msg": "successful!"}), 200
    return response

#role: 110
@api.route('/user/<int:id>/managePro/', methods = ['POST'], endpoint = 'ManageProject')
@login_required(role = 2)
def manage_project(uid, id):
    newPList = request.get_json().get('projectList')
    oldPList = User2Project.query.filter_by(user_id = id).all()
    for pid in newPList:
        pjc = Project.query.filter_by(id = pid).first()
        if pjc not in oldPList:
            record = User2Project(user_id = id, project_id = pid)
            db.session.add(record)
    for pjc in oldPList:
        if pjc.id not in newPList:
            record = User2Project.query.filter_by(user_id = id, project_id = pid).first()
            if record is not None:
                try:
                    db.session.delete(record)
                except:
                    pass
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 110
@api.route('/user/<int:id>/manageGroup/', methods = ['POST'], endpoint = 'ManageGroup')
@login_required(role = 2)
def manage_group(uid, id):
    gid = request.get_json().get('groupID')
    usr = User.query.filter_by(id = id).first()
    usr.group_id = gid
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200.
    return response

#role: 100
@api.route('/user/<int:id>/setRole/', methods = ['POST'], endpoint = 'SetRole')
@login_required(role = 4)
def set_role(uid, id):
    role = request.get_json().get('role')
    usr = User.query.filter_by(id = id).first()
    usr.role = role
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

#role: 001
@api.route('/user/<int:id>/setting/', methods = ['GET'], endpoint = 'GetSetting')
@login_required(role = 1)
def get_setting(uid, id):
    if id == uid:
        user = User.query.filter_by(id = uid).first()
        response = jsonify({
            "name": user.name,
            "email": user.email,
            "tel": user.tel,
            "avatar": user.avatar,
            "email_service": user.email_service,
            "message": user.message,
        })
        response.status_code = 200
        return response
    else:
        request_user = User.query.filter_by(id = uid).first()
        got_user = User.query.filter_by(id = id).first()
        if request_user.role == 0:
            response = jsonify({
                "msg": 'please get yourself information!',
            })
            response.status_cocde = 402
            return response
        else:
            response = jsonify({
                "name": got_user.name,
                "avatar": got_user.avatar,
                "email": got_user.email,
                "tel": got_user.tel,
                "email_service": got_user.email_service,
                "message": got_user.message,
            })
        response.status_code = 200
        return response

#role: 001
@api.route('/user/<int:id>/setting/', methods = ['POST'], endpoint = 'EditSetting')
@login_required(role = 1)
def editsetting(uid, id):
    if uid !=  id:
        response = jsonify({
            "msg": 'this is others personal setting!', 
        })
        response.status_code = 401
        return response

    username = request.get_json().get('username')
    address = request.get_json().get('address')
    tel = request.get_json().get('tel')
    email = request.get_json().get('email')
    message = request.get_json().get('message')

    # 2019.01.25 new:
    testU = User.query.filter_by(name=username).first()
    if testU != None:
        return jsonify({"msg": "Username has existed!"}), 403

    usr = User.query.filter_by(id = id).first()
    usr.name = username
    usr.email = address
    usr.tel = tel
    usr.email_service = email
    usr.message = message
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response
    
#role: 001
@api.route('/user/uploadAvatar/', methods = ['POST'], endpoint = 'UploadAvatar')
@login_required(role = 1)
def upload_avatar(uid):
    usr = User.query.filter_by(id = uid).first()
    image = request.files.get('image')
    try:
        filename = secure_filename(image.filename) + str(time.time())
        image.save(os.path.join(os.getcwd(), filename))
        key = filename
        localfile = os.path.join(os.getcwd(), filename)
        res = qiniu_upload(key, localfile)
        i = res.find('com')
        res = 'http://' + res[:i + 3] + '/' + res[i + 3:]
        os.system('rm -rf '+ filename)
        usr.avatar = res
        db.session.add(usr)
        db.session.commit()
        response = jsonify({
            "url": res,
        })
        print (res)
        response.status_code = 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 403
    return response

# role 110
@api.route('/user/<int:id>/', methods = ['DELETE'], endpoint = 'DeleteMember')
@login_required(role = 2)
def delete_member(uid,id):
    if uid == id :
        response = jsonify({
            "msg": 'Never give up yourself!',
        })
        response.status_code = 402
        return response
    usr = User.query.filter_by(id=id).first()
    usr.role = 0
    grp = Group.query.filter_by(id=usr.group_id).first()
    team = Group.query.filter_by(id=usr.team_id).first()
    if grp is not None:
        grp.count -= 1
        db.session.add(grp)
    if team is not None:
        team.count -= 1
        db.session.add(team)
    usr.team_id = None
    usr.group_id = None
    db.session.add(usr)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

# role 110
@api.route('/team/applyList/', methods = ['GET'], endpoint = 'ApplyList')
@login_required(role = 2)
def apply_list(uid):
    usrs = db.session.query(Apply).all()
    l = list([])
    if usrs is None:
        response = jsonify({
            "msg": 'Application all done!',
        })
        response.status_code = 201
        return response
    for a in usrs:
        user = User.query.filter_by(id = a.user_id).first()
        if user.role == 0:
            l.append({
                "userID": user.id,
                "userName": user.name,
                "userEmail": user.email,
            })
    response = jsonify({
        "list": l,
    })
    response.status_code = 200
    return response

# role: 110
@api.route('/team/apply/<int:id>/', methods = ['DELETE'], endpoint = "RefuseApply")
@login_required(role = 2)
def refuse_apply(uid,id):
    record = Apply.query.filter_by(user_id = id).first()
    if record is None:
        response = jsonify({})
        response.status_code = 403
        return response
    db.session.delete(record)
    db.session.commit()
    response = jsonify({})
    response.status_code = 200
    return response

# role: 001
@api.route('/team/invite/', methods = ['GET'], endpoint = 'GetInviteLink')
@login_required(role = 1)
def get_invite_link(uid):
    usr = User.query.filter_by(id = uid).first()
    teamID = usr.team_id
    team = Team.query.filter_by(id = teamID).first()
    s = Serializer(current_app.config['SECRET_KEY'])
    hash_id = s.dumps({'teamID': team.id}).decode('utf-8')
    response = jsonify({
        "invite_url": "/team/invite/?hash_id=" + hash_id,
        "hash_id": hash_id,
    })
    response.status_code = 200
    return response

# role: 000
@api.route('/team/invite/<string:hash_id>', methods = ['GET'], endpoint = 'GetTeamID')
def get_team_id():
    hash_id = request.args.get('hash_id')
    if hash_id is None:
        response = jsonify({
            'msg': 'Your hash_id ??? Where??',
        })
        response.status_code = 403
        return response
    t = hash_id.encode('utf-8')
    s=Serializer(current_app.config['SECRET_KEY'])
    try:
        data=s.loads(t)
    except:
        abort(402)
    tid=data.get('teamID')
    response = jsonify({
        'teamID': tid,
    })
    response.status_code = 200
    return response