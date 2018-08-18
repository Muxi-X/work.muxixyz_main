from flask import jsonify,request,current_app,url_for
from . import api
from .. import db
from ..models import Team,Group,User,Project,Message,Statu,File,Comment
from ..decorator import login_required


@api.route('/group/new/',methods=['POST'])
@login_required
def NewGroup(uid):
    role=8 # 1000
    usr=User.query.filter_by(id=uid).first()
    if usr.role|role is not role:
        response=jsonify({
            "msg": 'you are not superuser!',
        })
        response.status_code=401
        return response 
    gname=request.get_json().get('groupName')
    ulist=request.get_json().get('userlist')
    group=Group(name=gname,count=0)
    db.session.add(group)
    db.session.commit()
    for u in ulist:
        usr=User.query.filter_by(id=u).first()
        if usr is None:
            continue
        group.count+=1
        usr.group_id=group.id
        db.session.add(usr)
    db.session.add(group)
    db.session.commit()
    response=jsonify({
        "msg": 'successful!',
    })
    response.status_code=200
    return response

@api.route('/group/<int: gid>/userList',methods=['GET'])
@login_required
def GroupUserList(uid,gid):
    page=1
    if request.args.get('page') is not None:
        page=int(request.args.get('page'))
    grp=Group.query.filter_by(id=gid).first()
    counter=0
    usrs=list([None,None,None,None,None,None,None,None,None,None,None])
    for u in grp.users:
        c=int(counter)//10
        if (c+1) ==page:
            usrs[counter%10]={
                "username": u.name,
                "userID": u.id,
                "role": u.role,
                "email": u.email,
            }
        counter+=1
    response=jsonify({
                 "count": counter,
                 "list": usrs,
             })
    response.status_code=200
    return response

@api.route('/group/list',methods=['GET'])
@login_required
def GroupList(uid):
    gid=1
    l=list([])
    while True:
        grp=Group.query.filter_by(id=gid).first()
        if grp is None:
            break
        l.append({
            "groupID": gid,
            "groupName": grp.name,
            "userCount": grp.count,
        })
        gid+=1
    response=jsonify({
        "groupList": l,
    })
    response.status_code=200
    return response

@api.route('/project/<int: pid>/userList/',methods=['GET'])
@login_required
def ProjectUserList(uid,pid):
    page=1
    if request.args.get('page') is not None:
        page=int(request.args.get('page'))
    pjt=Project.query.filter_by(id=pid).first()
    counter=0
    usrs=list([None,None,None,None,None,None,None,None,None,None,None])
    for u in pjc.users:
        c=int(counter)//10
        if (c+1) ==page:
            usrs[counter%10]={
                "username": u.name,
                "userID": u.id,
                "avatar": u.avatar,
            }
        counter+=1
    response=jsonify({
                 "count": counter,
                 "list": usrs,
             })
    response.status_code=200
    return response

@api.route('/project/list/',methods=['GET'])
@login_required
def ProjectList(uid):
	role=14 #1110
    usr=User.query.filter_by(id=uid).first()
    if usr.role|role is not role:
        response=jsonify({
            "msg": 'you just are a member!',
        })
        response.status_code=401
        return response
    pid=1
    l=list([])
    while True:
        pjc=Project.query.filter_by(id=gid).first()
        if pjc is None:
            break
        l.append({
            "projectID": pid,
            "peojectName": pjc.name,
            "userCount": pjc.count,
        })
        pid+=1
    response=jsonify({
        "projectList": l,
    })
    response.status_code=200
    return response

