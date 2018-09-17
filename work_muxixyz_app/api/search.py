from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Team, Group, User, Project, User2Project, Messgae, Statu, File, Doc, Comment, Apply
from ..decorator import login_required
from ..timetools import to_readable_time
from ..mq import newfeed
import time

def takeKey(dic):
    return dic.get('time')

@api.route("/search/", methods = ['POST'], endpoint = 'Search')
@login_required(role = 1)
def search(uid):
    page = 1
    pageSize = 10
    if request.args.get('page') is not None:
        page = int(request.args.get('page'))
    pattern = request.get_json().get('pattern')
    projectID = request.get_json().get('projectID')
    files = File.filename.like('%'+pattern+'%')
    docs = Doc.filename.like('%'+pattern)+'%')
    l = list([])
    if projectID > 0:
        projectName = Project.query.filter_by(id = projectID).first().name
    if files is not None:
        for file in files:
            if projectID == 0:
                continue
            elif file.project_id == projectID:
                projectName = Project.query.filter_by(id = projectID).first().name
                l.append({
                    "kind": 1,
                    "sourceID": file.id,
                    "recordName": file.filename,
                    "projectID": projectID,
                    "projectName": projectName,
                    "creator": User.query.filter_by(id = file.creator_id).first().name,
                    "time": file.create_time,
                })
    if docs is not None:
        for doc in docs:
            if projectID == 0:
                continue
            elif doc.project_id == projectID:
                projectName = Project.query.filter_by(id = projectID).first().name
                l.append({
                    "kind": 1,
                    "sourceID": doc.id,
                    "recordName": doc.filename,
                    "projectID": projectID,
                    "projectName": projectName,
                    "creator": User.query.filter_by(id = doc.creator_id).first().name,
                    "time": doc.create_time,
                })
    l.sort(key = takeKey, reverse = True)
    recordNum = len(l)
    pageMax = recordNum / pageSize
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
