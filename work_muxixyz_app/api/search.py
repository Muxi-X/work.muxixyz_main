from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..page import get_rows
from ..models import Team, Group, User, Project, User2Project, Message, Statu, File, Doc, Comment, Apply
from ..decorator import login_required
from ..timetools import to_readable_time
from ..mq import newfeed
import time

def takeKey(dic):
    return dic.get('time')

@api.route("/search/", methods = ['POST'], endpoint = 'Search')
@login_required(role = 1)
def search(uid):

    ''' Check the project list, to make sure the information which be returned
        is secure. And check is that project exist.

        Status Code:   200   OK
                       201   OK but get none information
                       401   Unauth
                       403   ProjectMistake

    '''
    page = 1
    pageSize = 10
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    pattern = request.get_json().get('pattern')
    projectID = request.get_json().get('projectID')

    pL = {}
    usr = User.query.filter_by(id = uid).first()

    if projectID == 0:
        # 2019.01.28 new
        if usr.role == 1:
            recordList = User2Project.query.filter_by(user_id = uid).all()
            if recordList is not None:
                for record in recordList:
                    project = Project.query.filter_by(id=record.project_id).first()
                    pL[project.id] = project.name
        if usr.role >= 3:
            projectList = get_rows(Project, None, None, page, pageSize)['dataList']
            for p in projectList:
                pL[p.id] = p.name
        if len(pL.keys()) == 0:
            return jsonify({"msg": "You're already not join any project!"}), 403
    else:
        project = Project.query.filter_by(id = projectID).first()
        if project is not None:
            pL[project.id] = project.name
        else:
            return jsonify({"msg": "project not existed!"}), 403

    files = File.query.filter(File.filename.like("%"+pattern+"%")).all()
    docs =  Doc.query.filter(Doc.filename.like("%"+pattern+"%")).all()

    l = list([])
    if files is not None:
        for file in files:
            if file.project_id in pL.keys():
                l.append({
                    "kind": 1,
                    "sourceID": file.id,
                    "recordName": file.realname,
                    "projectID": file.project_id,
                    "projectName": pL[file.project_id],
                    "creator": User.query.filter_by(id = file.creator_id).first().name,
                    "time": file.create_time,
                })
    if docs is not None:
        for doc in docs:
            if doc.project_id in pL.keys():
                l.append({
                    "kind": 0,
                    "sourceID": doc.id,
                    "recordName": doc.filename,
                    "projectID": doc.project_id,
                    "projectName": pL[doc.project_id],
                    "creator": User.query.filter_by(id = doc.creator_id).first().name,
                    "time": doc.create_time,
                })

    l.sort(key = takeKey, reverse = True)
    recordNum = len(l)
    pageMax = type(1)(recordNum / pageSize)
    if recordNum % pageSize != 0:
        pageMax += 1
    hasNext = True
    if page == pageMax:
        hasNext = False
        l = l[pageSize*(page-1):]
    else:
        l = l[pageSize*(page-1):pageSize*page]

    response = jsonify({
        "count": recordNum,
        "pageMax": pageMax,
        "pageNow": page,
        "hasNext": hasNext,
        "list": l,
    })
    response.status_code = 200
    return response
