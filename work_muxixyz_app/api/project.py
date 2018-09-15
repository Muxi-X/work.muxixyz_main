from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import User, Project, Comment, User2Project, FolderForFile, FolderForMd, Doc, File
from ..decorator import login_required
import time
from ..mq import newfeed
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
import os

access_key = os.environ.get('ACCESS_KEY')
secret_key = os.environ.get('SECRET_KEY')
url = os.environ.get('URL')
bucket_name = 'test-work'
q = qiniu.Auth(access_key, secret_key)
bucket = BucketManager(q)


@api.route('/project/new/', methods=['POST'], endpoint='ProjectNew')
@login_required(role=2)
def project_new(uid):
    username = request.get_json().get('username')
    projectname = request.get_json().get('projectname')
    userlist = request.get_json().get('userlist')
    intro = request.get_json().get('intro')

    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    count = len(userlist)
    user = User.query.filter_by(id=uid).first()
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
            "errmsg": str(e)
        }), 500
    newfeed(uid, "create" + projectname, 1, project.id)
    return jsonify({
        "project_id": str(project.id)
    }), 201


@api.route('/project/<int:pid>/', methods=['POST'], endpoint='ProjectPidPost')
@login_required(role=2)
def project_pid_post(uid, pid):
    intro = request.get_json().get('intro')
    name = request.get_json().get('name')

    try:
        project = Project.query.filter_by(id=pid).first()
        project.name = name
        project.intro = intro

        db.session.add(project)
        db.session.commit()
    except Exception as e:
        print(e)
        return jsonify({
            "errormesage": str(e)
        }), 500
    newfeed(uid, "revise" + name, 1, project.id)
    return jsonify({
    }), 201


@api.route('/project/<int:pid>/', methods=['DELETE'], endpoint='ProjectPidDelete')
@login_required(role=2)
def project_pid_delete(uid, pid):
    try:
        project = Project.query.filter_by(id=pid).first()
        db.session.delete(project)
        db.session.commit()
        user2projects = User2Project.query.filter_by(project_id=pid)
        for u2p in user2projects:
            db.session.delete(u2p)
        db.session.commit()

        files = File.query.filter_by(project_id=pid)
        for file in files:
            db.session.delete(file)
        db.session.commit()

        docs = Doc.query.filter_by(project_id=pid)
        for doc in docs:
            db.session.delete(doc)
        db.session.commit()

        folders1 = FolderForFile.query.filter_by(project_id=pid).all()
        for folder in folders1:
            db.session.delete(folder)

        folders2 = FolderForMd.query.filter_by(project_id=pid).all()
        for folder in folders2:
            db.session.delete(folder)

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, "delete" + project.name, 1, project.id)
    return jsonify({
    }), 200


@api.route('/project/<int:pid>/', methods=['GET'], endpoint='ProjectPidGet')
@login_required(role=1)
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
            "errmsg": str(e)
        }), 500


@api.route('/project/<int:pid>/member/', methods=['PUT'], endpoint='ProjectMemberPut')
@login_required(role=2)
def project_member_put(uid, pid):
    userlist = request.get_json().get('userList')
    try:
        project = Project.query.filter_by(id=pid).first()
        project.count += len(userlist)
        db.session.add(project)
        u2ps = User2Project.query.filter_by(project_id=pid).all()
        nu = []
        for u2p in u2ps:
            if u2p.user_id in userlist:
                nu.append(u2p.user_id)
                continue
            db.session.delete(u2p)
        db.session.commit()
        for user in userlist:
            if user in nu:
                continue
            nuser = User2Project(
                user_id=user,
                project_id=pid
            )
            db.session.add(nuser)
        db.session.commit()
    except Exception as e:
        print (e)
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, "add member of" + project.name, 1, project.id)
    return jsonify({
    }), 200


@api.route('/project/<int:pid>/member/', methods=['GET'], endpoint='ProjectMemberGet')
@login_required(role=1)
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

# --------/------------------------------
@api.route('/project/<int:pid>/doc/<int:fid>/comments/', methods=['POST'], endpoint='ProjectDocCommentsPost')
@login_required(role=1)
def project_doc_comments_post(uid, pid, fid):
    import time
    content = request.get_json().get('content')
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    comment = Comment(
        kind=1,
        content=content,
        time=localtime,
        creator=uid,
        doc_id=fid
    )
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, "create comment", 1, comment.id)
    return jsonify({
        "cid": str(comment.id)
    }), 201


@api.route('/project/<int:pid>/file/<int:fid>/comments/', methods=['GET'], endpoint='ProjectFileCommentsGet')
@login_required(role=1)
def project_file_comments_get(uid, pid, fid):
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
            "errmsg": str(e)
        }), 500
    return jsonify({
        "commentList": commentList
    })


@api.route('/project/<int:pid>/file/<int:fid>/comment/<int:cid>/', methods=['GET'], endpoint='ProjectFileCommentGet')
@login_required(role=1)
def project_file_comment_get(uid, pid, fid, cid):
    try:
        comment = Comment.query.filter_by(id=cid).first()
        creator = User.query.filter_by(id=comment.creator).first()
        username = creator.name
        avatar = creator.avatar
        time = Comment.time
        content = comment.content
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    return jsonify({
        "username": username,
        "avatar": avatar,
        "time": time,
        "content": content
    }), 200


@api.route('/project/<int:pid>/file/<int:fid>/comment/<int:cid>/', methods=['DELETE'], endpoint='ProjectFileCommentDelete')
@login_required(role=1)
def project_file_comment_delete(uid, pid, fid, cid):
    try:
        if comment.creator != uid:
            return jsonify({}), 401
        comment = Comment.query.filter_by(id=cid).first()
        db.session.delete(comment)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    newfeed(uid, "delete comment", 1, comment.id)
    return jsonify({
    }), 200


@api.route('/folder/filetree/<int:pid>/', methods=['PUT'], endpoint='FileTreePut')
@login_required(role=1)
def file_tree_put(uid, pid):
    filetree = request.get_json().get('filetree')
    try:
        project = Project.query.filter_by(id=pid).first()
        project.filetree = filetree
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })
    return jsonify({}), 200


@api.route('/folder/filetree/<int:pid>/', methods=['GET'], endpoint='FileTreeGet')
@login_required(role=1)
def file_tree_get(uid, pid):
    try:
        return jsonify({
            "filetree": Project.query.filter_by(id=pid).first().filetree
        })
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })


@api.route('/folder/doctree/<int:pid>/', methods=['PUT'], endpoint='DocTreePut')
@login_required(role=1)
def file_tree_put(uid, pid):
    doctree = request.get_json().get('doctree')
    try:
        project = Project.query.filter_by(id=pid).first()
        project.doctree = doctree
        db.session.add(project)
        db.session.commit()
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })
    return jsonify({}), 200


@api.route('/folder/doctree/<int:pid>/', methods=['GET'], endpoint='DocTreeGet')
@login_required(role=1)
def file_tree_get(uid, pid):
    try:
        return jsonify({
            "filetree": Project.query.filter_by(id=pid).first().doctree
        })
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })