from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Team, Group, User, Project, Message, Statu, File, Folder, Comment, User2Project
from ..decorator import login_required
import time
from ..mq import newfeed
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config

access_key = 'YCdnGHp2tRa7V0KDisHqXehlny0eVNM5vQow1cQV'  # os.environ.get('ACCESS_KEY)
secret_key = 'ZGgkaNPunh6Y32FcsAtvhOd61rnlcKeeXPZ-qIlr'  # os.environ.get('SECRET_KEY)
url = 'pdw7hnao1.bkt.clouddn.com'                        # os.environ.get('URL')
bucket_name = 'test-work'
q = qiniu.Auth(access_key, secret_key)
bucket = BucketManager(q)


@api.route('project/new/', methods=['POST'], endpoint='ProjectNew')
@login_required(role = 2)
def project_new(uid):
    username = request.get_json().get('username')
    projectname = request.get_json().get('projectname')
    userlist = request.get_json().get('userlist')
    intro = request.get_json().get('intro')

    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    count = len(userlist)
    user = User.query.filter_by(name=username).first()
    team_id = user.team_id

    project = Project(name=projectname,
                      intro=intro,
                      time=localtime,
                      count=count + 1,
                      team_id=team_id)

    try:
        db.session.add(project)
        db.session.commit()
        user2project = User2Project(
            user_id=user.id,
            project_id=project.id
        )
        db.session.add(user2project)
        db.session.commit()
        for puser in userlist:
            user2project = User2Project(
                user_id=puser['userID'],
                project_id=project.id
            )
            db.session.add(user2project)
            db.session.commit()
    except Exception as e:
        return jsonify({
            "errormessage": str(e)
        }), 500
    action = "create" + projectname
    kind = 1
    newfeed(uid, action, kind, project.id)
    return jsonify({
        'project_id': str(project.id)
    }), 201


@api.route('project/<int:pid>/', methods=['POST', 'DELETE'], endpoint='ProjectPid')
@login_required(role = 2)
def project_pid(uid, pid):
    if request.method == 'POST':
        intro = request.get_json().get('intro')
        name = request.get_json().get('name')

        try:
            project = Project.query.filter_by(id=pid).first()
            project.name = name
            project.intro = intro

            db.session.add(project)
            db.session.commit()
        except Exception as e:
            return jsonify({
                "errormesage": e
            }), 500
        action = "revise" + name
        kind = 1
        newfeed(uid, action, kind, project.id)
        return jsonify({
        }), 201
    elif request.method == 'DELETE':
        def folder_deleter(deid):
            defiles = File.query.filter_by(folder_id=deid, re=False).all()
            for de in defiles:
                ret, info = bucket.delete(bucket_name, de.filename)
                db.session.delete(de)
                db.session.commit()

            defolders = Folder.query.filter_by(father_id=deid, re=False).all()
            if len(defolders) == 0:
                defolder = Folder.query.filter_by(id=deid, re=False).first()
                db.session.delete(defolder)
                db.session.commit()
            else:
                for defo in defolders:
                    folder_deleter(defo.id)
        try:
            project = Project.query.filter_by(id=pid).first()
            db.session.delete(project)
            db.session.commit()
            user2projects = User2Project.query.filter_by(project_id=pid)
            for u2p in user2projects:
                db.session.delete(u2p)
            db.session.commit()
            files = File.query.filter_by(project_id=pid, folder_id=None)
            for file in files:
                db.session.delete(file)
            db.session.commit()
            folders = Folder.query.filter_by(project_id=pid, father_id=None).all()
            for fo in folders:
                try:
                    folder_deleter(fo.id)
                except Exception as e:
                    return jsonify({
                        "errormessage": str(e)
                    })
        except Exception as e:
            return jsonify({
                "errormessage": str(e)
            }), 500
        action = "delete" + project.name
        kind = 1
        newfeed(uid, action, kind, project.id)
        return jsonify({
        }), 200


@api.route('project/<int:pid>/', methods=['GET'], endpoint='ProjectPidGet')
@login_required(role = 1)
def project_pid_get(uid, pid):
    u2ps = User2Project.query.filter_by(user_id=uid).all()
    flag = True
    for u2p in u2ps:
        if u2p.project_id == pid:
            flag = False
            break
    if flag:
        return jsonify({}), 401
    try:
        project = Project.query.filter_by(id=pid).first()
        intro = project.intro
        name = project.name
        userCount = project.count
        return jsonify({
            "intro": intro,
            "name": name,
            "userCount": userCount
        }), 200
    except Exception as e:
        return jsonify({
            "errormessage": str(e)
        }), 500


@api.route('project/<int:pid>/member/', methods=['PUT'], endpoint='ProjectMemberPut')
@login_required(role = 2)
def project_member_put(uid, pid):
    userlist = request.get_json().get('userList')
    try:
        project = Project.query.filter_by(id=pid).first()
        project.count += len(userlist)
        db.session.add(project)
        for user in userlist:
            nuser = User2Project(
                user_id=user,
                project_id=pid
            )
            db.session.add(nuser)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errormessage": str(e)
        }), 500
    action = "add member of" + project.name
    kind = 1
    newfeed(uid, action, kind, project.id)
    return jsonify({
    }), 200


@api.route('project/<int:pid>/member/', methods=['GET'], endpoint='ProjectMemberGet')
@login_required(role = 1)
def project_member_get(uid, pid):
    try:
        memberList = []
        u2plist = User2Project.query.filter_by(project_id=pid).all()
        for u2p in u2plist:
            user = User.query.filter_by(id=u2p.user_id).first()
            memberList.append(
                {
                    "userID": user.id,
                    "username": user.name,
                    "avatar": user.avatar
                }
            )
    except Exception as e:
        print(e)
        return jsonify({
        }), 500
    return jsonify({
    }), 200


@api.route('project/<int:pid>/file/<int:fid>/comments/', methods=['POST', 'GET'], endpoint='ProjectFileComments')
@login_required(role = 1)
def project_file_comments(uid, pid, fid):
    if request.method == 'POST':
        import time
        content = request.get_json().get('content')
        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        comment = Comment(
            kind=1,
            content=content,
            time=localtime,
            creator=uid,
            file_id=fid
        )
        try:
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return jsonify({
                "errormessage": str(e)
            }), 500
        action = "create comment"
        kind = 1
        newfeed(uid, action, kind, comment.id)
        return jsonify({
            "cid": str(comment.id)
        }), 201
    elif request.method == 'GET':
        comments = Comment.query.filter_by(file_id=fid).all()
        commentList = []
        try:
            for comment in comments:
                creator = User.query.filter_by(id=comment.creator).first()
                username = creator.name
                avatar = creator.avatar
                time = comment.time
                content = comment.content
                commentList.append(
                    {
                        "username": username,
                        "avatar": avatar,
                        "time": time,
                        "content": content
                    }
                )
        except Exception as e:
            return jsonify({
                "errormessage": str(e)
            }), 500
        return jsonify({
            "commentList": commentList
        })
    else:
        return jsonify({
        }), 403


@api.route('project/<int:pid>/file/<int:fid>/comment/<int:cid>/', methods=['GET', 'DELETE'], endpoint='ProjectFileComment')
@login_required(role = 1)
def project_file_comment_get(uid, pid, fid, cid):
    if request.method == 'GET':
        try:
            comment = Comment.query.filter_by(id=cid).first()
            creator = User.query.filter_by(id=comment.creator).first()
            username = creator.name
            acatar = creator.avatar
            time = Comment.time
            content = comment.content
        except Exception as e:
            return jsonify({
                "errormessage": str(e)
            })
        return jsonify({
        }), 200
    elif request.method == 'DELETE':
        try:
            if comment.creator != uid:
                return jsonify({}), 401
            comment = Comment.query.filter_by(id=cid).first()
            db.session.delete(comment)
            db.session.commit()
        except Exception as e:
            return jsonify({
                "errormessage": str(e)
            })
        action = "delete comment"
        kind = 1
        newfeed(uid, action, kind, comment.id)
        return jsonify({
        }), 200
    else:
        return jsonify({
        }), 403