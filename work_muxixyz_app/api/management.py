from flask import jsonify,request,current_app,url_for
from . import api
from .. import db
from ..models import Team,Group,User,Project,User2Project,Message,Statu,File,Comment
from ..decorator import login_required

import requests

#role: 100
@api.route('/group/new/',methods=['POST'])
@login_required
def NewGroup(uid):
    role=4 # 100
    usr=User.query.filter_by(id=uid).first()
    if usr.role|role != role:
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

#role: 001
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

#role: 001
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

#role: 001
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

#role: 110
@api.route('/project/list/',methods=['GET'])
@login_required
def ProjectList(uid):
    role=6 #110
    usr=User.query.filter_by(id=uid).first()
    if usr.role|role != role:
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

#role: 001
@api.route('/user/project/list/',methods=['GET'])
@login_required
def UserProjectList(uid):
    page=1
    if request.args.get('page') is not None:
        page=int(request.args.get('page'))
    counter=0
    pjcs=list([None,None,None,None,None,None,None,None,None,None,None])
# page     
    usr=User.query.filter_by(id=uid).first()
    if usr.role > 1:
        response=requests.get(
            url_for('api.ProjectList',_external=True),
            headers={
                "token": request.headers.get('token'),
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        )
    for p in usr.projects:
        c=int(counter)//10
        if (c+1) ==page:
            usrs[counter%10]={
                "projectID": p.id,
                "projectName": p.name,
                "userCount": p.count,
            }
        counter+=1
    response=jsonify({
        "count": counter,
        "list": pjcs,
    })
    response.status_code=200
    return response

#role: 110
@api.route('/user/2bmember/',methods=['POST'])
@login_required
def User2bMember(uid):
    usr=User.query.filter_by(id=uid).first()
    role=6
    if usr.role|role != role:
        response=jsonify({
            "msg": 'you are not superuser or admin!',
        })
        response.status_code=401
        return response
# role    
    if usr.role != 0:
        response=jsonify({
            "msg": 'user already be a member!',
        })
        response.status_code=402
        return response
    usr.role=1
    db.session.add(usr)
    db.session.commit()
    response=jsonify({
        "msg": 'successful!',
    })
    response.status_code=200
    return response

#role: 100
@api.route('/user/addAdmin/',methods=['POST'])
@login_required
def AddAdmin(uid):
    usr=User.query.filter_by(id=uid).first()

    role=4
    if role|usr.role != role:
        response=jsonify({
            "msg": 'you are not superuser!'
        })
        response.status_code=401
        return response
    lname=request.get_json().get('luckydog')
    luckydog=User.query.filter_by(name=lname).first()
    luckydog.role=3
    db.session.add(luckydog)
    db.session.commit()
    response=jsonify({})
    response.status_code=200
    return response

#role: 110
@api.route('/user/<int: id>/managePro/',methods=['POST'])
@login_required
def ManageProject(uid,id):
    role=6 #110
    usr=User.query.filter_by(id=uid).first()
    if role|usr.role != role:
        response=jsonify({
            "msg": 'you are not superuser or admin!',
        })
        response.status_code=401
        return response

    newPList=request.get_json().get('projectList')
    oldPList=User2Project.query.filter_by(user_id=id).all()
    for pid in newPList:
        pjc=Project.query.filter_by(id=pid).first()
        if pjc in oldPList && !(pjc in newPList):
            record=User2Project.query.filter_by(user_id=id,project_id=pid).first()
            db.session.delete(record)
        if !(pjc in oldPList) && pjc in newPList:
            record=User2Project(user_id=id,project_id=pid)
            db.session.add(record)
    db.session.commit()
    responseh=jsonify({})
    response.status_code=200
    return response

#role: 110
@api.route('/user/<int: id>/manageGroup/',methods=['POST'])
@login_required
def ManageGroup(uid,id):
    usr=User.query.filter_by(id=uid).first()
    role=6 #110
    if role|usr.role != role:
        response=jsonify({
            "msg": 'you are not superuser or admin',
        })
        response.status_code=401
        return response

    gid=request.get_json().get('groupID')
    usr=User.query.filter_by(id=id).first()
    usr.group_id=gid
    db.session.add(usr)
    db.session.commit()
    response=jsonify({})
    response.status_code=200.
    return response

#role: 100
@api.route('/user/<int: id>/setRole/',methods=['POST'])
@login_required
def SetRole(uid,id):
    usr=User.query.filter_by(id=uid).first()
    role=4
    if role|usr.role != role:
        response=jsonify({
            "msg": 'you are not a superuser!',
        })
        response.status_code=401
        return response

    role=request.get_json().get('role')
    usr=User.query.filter_by(id=id).first()
    usr.role=role
    db.session.add(usr)
    db.session.commit()
    response=jsonify({})
    response.status_code=200
    return response

#role: 0001
@api.route('/user/<int: id>/setting/',methods=['POST'])
@login_required
def Setting(uid,id):
    if uid != id:
        response=jsonify({
        	"msg": 'this is others personal setting!',
        })
        response.status_code=401
        return response

    username=request.get_json().get('username')
    address=request.get_json().get('address')
    tel=reqruest.get_json().get('tel')
    email=request.get_json().get('email')
    message=request.get_json().get('message')
    usr=User.query.filter_by(id=id).first()
    usr.username=username
    usr.email=address
    usr.tel=tel
    usr.email_service=email
    usr.message=message
    db.session.add(usr)
    db.session.commit()
    response=jsonify({})
    response.status_code=200
    return response
