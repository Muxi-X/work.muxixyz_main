# -*- coding: utf-8 -*-
from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import User, Project, Comment, User2Project, FolderForFile, FolderForMd, Doc, File, Group
from ..decorator import login_required
import time
from ..mq import newfeed
from ..GenerateMsg import MakeMsg
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
import os

actions = ["加入", "创建", "编辑", "删除", "评论", "移动"]
sourceidmap = {
            "团队": 1,
            "项目": 2,
            "文档": 3,
            "文件": 4,
            "文件夹": 5,
            "进度": 6
        }


access_key = os.environ.get('WORKBENCH_ACCESS_KEY')
secret_key = os.environ.get('WORKBENCH_SECRET_KEY')
url = os.environ.get('WORKBENCH_URL')
bucket_name = 'ossworkbench'
q = qiniu.Auth(access_key, secret_key)
bucket = BucketManager(q)

def checkid(uid, pid):
    user = User.query.filter_by(id=uid).first()
    if user.role > 0:
        return True
    u2p = User2Project.query.filter_by(user_id=uid, project_id=pid).first()
    if u2p is None:
        return False

@api.route('/project/new/', methods=['POST'], endpoint='ProjectNew')
@login_required(role = 2)
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
    newfeed(uid, actions[0], projectname, sourceidmap["项目"], project.id, project.id, projectname)
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
            "errmsg": str(e)
        }), 500
    # newfeed(uid, actions[2], name, sourceidmap["项目"], project.id, project.id)
    return jsonify({
    }), 201


@api.route('/project/<int:pid>/', methods=['DELETE'], endpoint='ProjectPidDelete')
@login_required(role=2)
def project_pid_delete(uid, pid):
    try:
        project = Project.query.filter_by(id=pid).first()
        user2projects = User2Project.query.filter_by(project_id=pid)
        for u2p in user2projects:
            db.session.delete(u2p)
        db.session.commit()

        files = File.query.filter_by(project_id=pid).all()
        for file in files:
            ret, info = bucket.delete(bucket_name, file.filename)
            db.session.delete(file)
        db.session.commit()

        docs = Doc.query.filter_by(project_id=pid).all()
        for doc in docs:
            db.session.delete(doc)
        db.session.commit()

        folders1 = FolderForFile.query.filter_by(project_id=pid).all()
        for folder in folders1:
            db.session.delete(folder)
        db.session.commit()

        folders2 = FolderForMd.query.filter_by(project_id=pid).all()
        for folder in folders2:
            db.session.delete(folder)
        db.session.commit()

        name = project.name
        id = project.id

        db.session.delete(project)
        db.session.commit()

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, actions[3], project.name, sourceidmap["项目"], project.id, project.id, project.name)
    return jsonify({
    }), 200


@api.route('/project/<int:pid>/', methods=['GET'], endpoint='ProjectPidGet')
@login_required(role = 1)
def project_pid_get(uid, pid):
    if not checkid(uid, id):
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
@login_required(role = 2)
def project_member_put(uid, pid):
    userlist = request.get_json().get('userList')
    try:
        project = Project.query.filter_by(id=pid).first()
        project.count = len(userlist)
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
            newfeed(uid, actions[0], project.name, sourceidmap["项目"], project.id, project.id, project.name)
            db.session.add(nuser)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500
    # newfeed(uid, u"编辑" + project.name + '的成员', 1, project.id)
    return jsonify({
    }), 200


@api.route('/project/<int:pid>/member/', methods=['GET'], endpoint='ProjectMemberGet')
@login_required(role = 1)
def project_member_get(uid, pid):
    try:
        memberList = []
        u2plist = User2Project.query.filter_by(project_id=pid).all()
        for u2p in u2plist:
            user = User.query.filter_by(id=u2p.user_id).first()
            group = Group.query.filter_by(id=user.group_id).first()
            if group is not None:
                group_name = group.name
            else:
                group_name = None
            memberList.append(
                {
                    "userID": user.id,
                    "username": user.name,
                    "avatar": user.avatar,
                    "group": group_name,
                    "role": user.role
                }
            )
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500
    return jsonify({
        "memberList": memberList
    }), 200

# 文档评论

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
        return jsonify({
            "errmsg": str(e)
        }), 500
    curdoc = Doc.query.filter_by(id=fid).first();
    project = Project.query.filter_by(id = curdoc.project_id).first()
    newfeed(uid, actions[4], curdoc.filename, sourceidmap["文档"], curdoc.id, curdoc.project_id, project.name)
    MakeMsg(curdoc, uid, u"评论")
    return jsonify({
        "cid": str(comment.id)
    }), 201


@api.route('/project/<int:pid>/doc/<int:fid>/comments/<int:page>/', methods=['GET'], endpoint='ProjectDocCommentsGet')
@login_required(role=1)
def project_doc_comments_get(uid, pid, fid, page):
    comments = Comment.query.filter_by(doc_id=fid).all()
    commentList = []
    num = 0
    try:
        for comment in comments:
            num += 1
            if num > (page - 1) * 20 and num <= page * 20:
                creator = User.query.filter_by(id=comment.creator).first()
                username = creator.name
                avatar = creator.avatar
                mtime = comment.time
                content = comment.content
                cid = comment.id
                commentList.append(
                    {
                        "username": username,
                        "avatar": avatar,
                        "time": mtime,
                        "content": content,
                        "id": cid
                    }
                )
            elif num > page * 20:
                break
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500
    return jsonify({
        "commentList": commentList,
        "count": len(comments)
    })


@api.route('/project/<int:pid>/doc/<int:fid>/comment/<int:cid>/', methods=['GET'], endpoint='ProjectDocCommentGet')
@login_required(role=1)
def project_doc_comment_get(uid, pid, fid, cid):
    try:
        comment = Comment.query.filter_by(id=cid).first()
        creator = User.query.filter_by(id=comment.creator).first()
        username = creator.name
        avatar = creator.avatar
        mtime = Comment.time
        content = comment.content
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    return jsonify({
        "username": username,
        "avatar": avatar,
        "time": mtime,
        "content": content
    }), 200


@api.route('/project/<int:pid>/doc/<int:fid>/comment/<int:cid>/', methods=['DELETE'], endpoint='ProjectDocCommentDelete')
@login_required(role=1)
def project_doc_comment_delete(uid, pid, fid, cid):
    try:
        comment = Comment.query.filter_by(id=cid).first()
        id = comment.id
        if comment.creator != uid:
            return jsonify({}), 401
        db.session.delete(comment)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    return jsonify({
    }), 200

# 文件评论
@api.route('/project/<int:pid>/file/<int:fid>/comments/', methods=['POST'], endpoint='ProjectFileCommentsPost')
@login_required(role=1)
def project_file_comments_post(uid, pid, fid):
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
        return jsonify({
            "errmsg": str(e)
        }), 500
    curfile = File.query.filter_by(id=fid).first()
    project = Project.query.filter_by(id=curfile.project_id).first()
#    newfeed(uid, actions[4], curfile.realname, sourceidmap["文件"], curfile.id, curfile.project_id, project.name)
    MakeMsg(curfile, uid, u"评论")
    return jsonify({
        "cid": str(comment.id)
    }), 201


@api.route('/project/<int:pid>/file/<int:fid>/comments/<int:page>/', methods=['GET'], endpoint='ProjectFileCommentsGet')
@login_required(role=1)
def project_file_comments_get(uid, pid, fid, page):
    comments = Comment.query.filter_by(file_id=fid).all()
    commentList = []
    num = 0
    try:
        for comment in comments:
            num += 1
            if num > (page - 1) * 20 and num <= page * 20:
                creator = User.query.filter_by(id=comment.creator).first()
                username = creator.name
                avatar = creator.avatar
                mtime = comment.time
                content = comment.content
                cid = comment.id
                commentList.append(
                    {
                        "username": username,
                        "avatar": avatar,
                        "time": mtime,
                        "content": content,
                        "id": cid
                    }
                )
            elif num > page * 20:
                break
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500
    return jsonify({
        "commentList": commentList,
        "count": len(comments)
    })


@api.route('/project/<int:pid>/file/<int:fid>/comment/<int:cid>/', methods=['GET'], endpoint='ProjectFileCommentGet')
@login_required(role=1)
def project_file_comment_get(uid, pid, fid, cid):
    try:
        comment = Comment.query.filter_by(id=cid).first()
        creator = User.query.filter_by(id=comment.creator).first()
        username = creator.name
        avatar = creator.avatar
        mtime = Comment.time
        content = comment.content
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    return jsonify({
        "username": username,
        "avatar": avatar,
        "time": mtime,
        "content": content
    }), 200


@api.route('/project/<int:pid>/doc/<int:fid>/comment/<int:cid>/', methods=['DELETE'], endpoint='ProjectFileCommentDelete')
@login_required(role=1)
def project_file_comment_delete(uid, pid, fid, cid):
    try:
        comment = Comment.query.filter_by(id=cid).first()
        id = comment.id
        if comment.creator != uid:
            return jsonify({}), 401
        db.session.delete(comment)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    return jsonify({
    }), 200

@api.route('/folder/filetree/<int:pid>/', methods=['PUT'], endpoint='FileTreePut')
@login_required(role=1)
def file_tree_put(uid, pid):
    if not checkid(uid, pid):
        return jsonify({}), 401
    try:
        project = Project.query.filter_by(id=pid).first()
        filetree = request.get_json().get('filetree')
        project.filetree = filetree
        db.session.commit()
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })
    return jsonify({}), 200


@api.route('/folder/filetree/<int:pid>/', methods=['GET'], endpoint='FileTreeGet')
@login_required(role=1)
def file_tree_get(uid, pid):
    if not checkid(uid, pid):
        return jsonify({}), 401
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
    if not checkid(uid, pid):
        return jsonify({}), 401
    doctree = request.get_json().get('doctree')
    try:
        project = Project.query.filter_by(id=pid).first()
        project.doctree = doctree
        db.session.commit()
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })
    return jsonify({}), 200


@api.route('/folder/doctree/<int:pid>/', methods=['GET'], endpoint='DocTreeGet')
@login_required(role=1)
def file_tree_get(uid, pid):
    if not checkid(uid, pid):
        return jsonify({}), 401
    try:
        return jsonify({
            "doctree": Project.query.filter_by(id=pid).first().doctree
        })
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })
