from flask import jsonify,request,current_app,url_for
from . import api
from .. import db
from ..models import Team,Group,User,Project,Message,Statu,File,Comment
from ..decorator import login_required


@api.route('/group/new/',methods=['POST'])
@login_required
def NewGroup(uid):
	role=8
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


    