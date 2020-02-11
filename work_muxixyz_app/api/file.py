# -*- coding: UTF-8 -*-

from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Feed, Team, Group, User, Project, Message, Statu, File, Doc, FolderForFile, FolderForMd, Comment, \
    User2Project, User2File
from ..decorator import login_required
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
import os
import requests
import time
from ..mq import newfeed
from ..GenerateMsg import MakeMsg
from werkzeug import secure_filename

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

def qiniu_upload(key, localfile):
    token = q.upload_token(bucket_name, key, 3600)

    ret, info = qiniu.put_file(token, key, localfile)

    if ret:
        return '{0}{1}'.format(url, ret['key'])
    else:
        raise UploadError('上传失败，请重试')

def check(uid, C):
    user = User.query.filter_by(id=uid).first()
    if user.role > 0:
        return True
    pid = C.project_id
    u2p = User2Project.query.filter_by(user_id=uid, project_id=pid).first()
    if u2p is None:
        return False

def checkid(uid, pid):
    user = User.query.filter_by(id=uid).first()
    if user.role > 0:
        return True
    u2p = User2Project.query.filter_by(user_id=uid, project_id=pid).first()
    if u2p is None:
        return False


@api.route('/folder/file/', methods=['POST'], endpoint='FolderFilePost')
@login_required(role=1)
def folder_file_post(uid):
    try:
        foldername = request.get_json().get('foldername')
        project_id = request.get_json().get('project_id')

        if not checkid(uid, project_id):
            return jsonify({}), 401

        folderforfile = FolderForFile(
            name=foldername,
            create_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            create_id=uid,
            project_id=project_id
        )
        db.session.add(folderforfile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 500
    return jsonify({
        "id": str(folderforfile.id)
    }), 201


@api.route('/folder/file/<int:id>/', methods=['PUT'], endpoint='FolderFileIdPut')
@login_required(role=1)
def folder_file_id_put(uid, id):
    try:
        foldername = request.get_json().get('foldername')
        folderforfile = FolderForFile.query.filter_by(id=id).first()

        if not check(uid, folderforfile):
            return jsonify({}), 401

        folderforfile.name = foldername
        db.session.add(folderforfile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 500
    return jsonify({}), 200


@api.route('/folder/file/<int:id>/', methods=['DELETE'], endpoint='FolderFileIdDelete')
@login_required(role=1)
def folder_file_id_delete(uid, id):
    # name = FolderForFile.query.filter_by(id=id).first().name

    folder = request.get_json().get('folder')
    file = request.get_json().get('file')

    try:
        for folder_id in folder:
            folderforfile = FolderForFile.query.filter_by(id=folder_id).first()

            if not check(uid, folderforfile):
                return jsonify({}), 401

            folderforfile.re = True
            # db.session.delete(folderforfile)

        for file_id in file:
            file = File.query.filter_by(id=file_id).first()

            if not check(uid, file):
                return jsonify({}), 401
            # ret, info = bucket.delete(bucket_name, file.filename)         # 用于彻底删除，但是这里应该只是移动到回收站
            file.re = True
            file.delete_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.commit()

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({}), 200


@api.route('/folder/file/children/', methods=['POST'], endpoint='FolderFileChrildrenPost')
@login_required(role=1)
def folder_file_chrildren_post(uid):
    folder = request.get_json().get('folder')
    file_list = request.get_json().get('file')

    FolderList = []
    FileList = []
    try:
        for folder_id in folder:
            folderforfile = FolderForFile.query.filter_by(id=folder_id).first()

            check(uid, folderforfile)

            FolderList.append({
                "id": folderforfile.id,
                "name": folderforfile.name
            })

        for file_id in file_list:
            file = File.query.filter_by(id=file_id).first()

            if not check(uid, file):
                return jsonify({}), 401

            FileList.append({
                "id": file.id,
                "name": file.realname,
                "creator": User.query.filter_by(id=file.creator_id).first().name,
                "url": file.url,
                "create_time": file.create_time
            })
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({
        "FolderList": FolderList,
        "FileList": FileList
    }), 200


@api.route('/folder/doc/', methods=['POST'], endpoint='FolderDocPost')
@login_required(role=1)
def folder_doc_post(uid):
    try:
        foldername = request.get_json().get('foldername')
        project_id = request.get_json().get('project_id')

        if not checkid(uid, project_id):
            return jsonify({}), 401

        folderformd = FolderForMd(
            name=foldername,
            create_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            create_id=uid,
            project_id=project_id
        )
        db.session.add(folderformd)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({
        "id": str(folderformd.id)
    }), 201


@api.route('/folder/doc/<int:id>/', methods=['PUT'], endpoint='FolderDocIdPut')
@login_required(role=1)
def folder_doc_id_put(uid, id):
    try:
        foldername = request.get_json().get('foldername')
        folderformd = FolderForMd.query.filter_by(id=id).first()

        if not check(uid, folderformd):
            return jsonify({}), 401

        folderformd.name = foldername
        db.session.add(folderformd)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({}), 200


@api.route('/folder/doc/<int:id>/', methods=['DELETE'], endpoint='FolderDocIdDelete')
@login_required(role=1)
def folder_doc_id_delete(uid, id):
    # name = FolderForMd.query.filter_by(id=id).first().name

    folder = request.get_json().get('folder')
    doc = request.get_json().get('doc')

    try:
        for folder_id in folder:
            folderformd = FolderForMd.query.filter_by(id=folder_id).first()

            if not check(uid, folderformd):
                return jsonify({}), 401

            folderformd.re = True
            # db.session.delete(folderforfile)

        for doc_id in doc:
            doc = Doc.query.filter_by(id=doc_id).first()

            if not check(uid, doc):
                return jsonify({}), 401

            # ret, info = bucket.delete(bucket_name, doc.filename)         # 用于彻底删除，但是这里应该只是移动到回收站
            doc.re = True
        db.session.commit()

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({}), 200


@api.route('/folder/doc/children/', methods=['POST'], endpoint='FolderDocChrildrenPost')
@login_required(role=1)
def folder_doc_chrildren_post(uid):
    folder_list = request.get_json().get('folder')
    doc_list = request.get_json().get('doc')

    FolderList = []
    DocList = []
    try:
        for folder_id in folder_list:
            folderformd = FolderForMd.query.filter_by(id=folder_id).first()

            if not check(uid, folderformd):
                return jsonify({}), 401

            FolderList.append({
                "id": folderformd.id,
                "name": folderformd.name
            })

        for doc_id in doc_list:
            doc = Doc.query.filter_by(id=doc_id).first()

            if not check(uid, doc):
                return jsonify({}), 401

            DocList.append({
                "id": doc.id,
                "name": doc.filename,
                "lastcontent": doc.content[:100],
                "create_time": doc.create_time,
                "creator": User.query.filter_by(id=doc.creator_id).first().name
            })
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({
        "FolderList": FolderList,
        "DocList": DocList
    }), 200


@api.route('/editor/image/', methods=['POST'], endpoint='EditorImage')
@login_required(role=1)
def upload_image(uid):
    image = request.files.get('image')
    try:
        imagename = str(time.time()) + '.' + secure_filename(image.filename)
        image.save(os.path.join(os.getcwd(), imagename))
        key = imagename
        localfile = os.path.join(os.getcwd(), imagename)
        res = qiniu_upload(key, localfile)
        i = res.find('com')
        res = 'http://' + res[:i + 3] + '/' + res[i + 3:]
        os.remove(localfile)

        return jsonify({
            "image_url": res
        }), 200

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500


@api.route('/file/file/', methods=['POST'], endpoint='FileFilePost')
@login_required(role=1)
def file_file_post(uid):
    project_id = int(request.form.get('project_id'))

    if not checkid(uid, project_id):
        return jsonify({}), 401

    myfile = request.files.get('file')
    project = Project.query.filter_by(id=project_id).first()
    try:
        filename = str(time.time()) + '.' + secure_filename(myfile.filename)
        myfile.save(os.path.join(os.getcwd(), filename))
        key = filename
        localfile = os.path.join(os.getcwd(), filename)
        res = qiniu_upload(key, localfile)
        i = res.find('com')
        res = 'http://' + res[:i + 3] + '/' + res[i + 3:]
        os.remove(localfile)
        newfile = File(
            url=res,
            realname = myfile.filename,
            filename=filename,
            create_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            creator_id=uid,
            project_id=project_id,
        )
        db.session.add(newfile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 404
    newfeed(uid, actions[1], myfile.filename, sourceidmap["文件"], newfile.id, project_id, project.name)
    return jsonify({
        "fid": str(newfile.id),
        "name": myfile.filename
    }), 201


@api.route('/file/file/<int:id>/', methods=['PUT'], endpoint='FileFileIdPut')
@login_required(role=1)
def file_doc_id_put(uid, id):
    file = File.query.filter_by(id=id).first()

    if not check(uid, file):
        return jsonify({}), 401

    FileName = request.get_json().get('FileName')
    try:
        file.filename = FileName
        db.session.commit()
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        }), 404
    
    project = Project.query.filter_by(id=file.project_id).first()
    newfeed(uid, actions[2], FileName, sourceidmap["文件"], id, file.project_id, project.name)
    MakeMsg(file, uid, u"编辑")
    return jsonify({}), 200


@api.route('/file/file/<int:id>/', methods=['DELETE'], endpoint='FileFileIdDelete')
@login_required(role=2)
def file_file_id_delete(uid, id):
    try:
        file = File.query.filter_by(id=id).first()

        if not check(uid, file):
            return jsonify({}), 401

        file.re = True
        file.delete_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404

    project = Project.query.filter_by(id=file.project_id).first()
    newfeed(uid, actions[3], file.realname, sourceidmap["文件"], id, file.project_id, project.name)
    MakeMsg(file, uid, u"删除")

    # write by shiina
    record = User2File.query.filter_by(file_id = file.id, file_kind = 1).first()
    if record is not None:
        db.session.delete(record)
        db.session.commit()

    return jsonify({}), 200


@api.route('/file/doc/', methods=['POST'], endpoint='FileDocPost')
@login_required(role=1)
def file_doc_post(uid):
    mdname = request.get_json().get('mdname')
    mycontent = request.get_json().get('content')
    project_id = request.get_json().get('project_id')

    if not checkid(uid, project_id):
        return jsonify({}), 401

    project = Project.query.filter_by(id = project_id).first()
    try:
        newdoc = Doc(
            content=mycontent,
            filename=mdname,
            create_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            creator_id=uid,
            editor_id=uid,
            project_id=project_id,
        )
        db.session.add(newdoc)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 404
    newfeed(uid, actions[1], mdname, sourceidmap["文档"], newdoc.id, newdoc.project_id, project.name)
    record = User2File(user_id=uid, file_id=newdoc.id, file_kind=0)
    db.session.add(record)
    db.session.commit()
    return jsonify({
        "fid": str(newdoc.id)
    }), 201


@api.route('/file/doc/<int:id>/', methods=['DELETE'], endpoint='FileDocIdDelete')
@login_required(role=2)
def file_doc_id_delete(uid, id):
    try:
        doc = Doc.query.filter_by(id=id).first()

        if not check(uid, doc):
            return jsonify({}), 401

        doc.re = True
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404

    project = Project.query.filter_by(id=doc.project_id).first()
    # 同步删除之前有关此文档的动态
    Feed.query.filter(Feed.source_objectid == id).delete()
    newfeed(uid, actions[3], doc.filename, sourceidmap["文档"], doc.id, doc.project_id, project.name)
    MakeMsg(doc, uid, u"删除")

    # write by shiina
    record = User2File.query.filter_by(file_id = doc.id, file_kind = 0).first()
    if record is not None:
        db.session.delete(record)
        db.session.commit()

    return jsonify({}), 200


@api.route('/file/doc/<int:id>/', methods=['GET'], endpoint='FileDocIdGet')
@login_required(role=1)
def file_doc_id_get(uid, id):
    doc = Doc.query.filter_by(id=id).first()

    if not check(uid, doc):
        return jsonify({}), 401

    try:
        return jsonify({
            "name": doc.filename,
            "creator": User.query.filter_by(id=doc.creator_id).first().name,
            "content": doc.content,
            "lasteditor": User.query.filter_by(id=doc.editor_id).first().name,
            "create_time": doc.create_time,
        }), 200
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404


@api.route('/file/doc/<int:id>/', methods=['PUT'], endpoint='FileDocIdPut')
@login_required(role=1)
def file_doc_id_put(uid, id):
    doc = Doc.query.filter_by(id=id).first()

    if not check(uid, doc):
        return jsonify({}), 401

    DocName = request.get_json().get('DocName')
    content = request.get_json().get('content')
    try:
        doc.filename = DocName
        doc.content = content
        db.session.commit()
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        }), 404

    project = Project.query.filter_by(id=doc.project_id).first()
    newfeed(uid, actions[2], doc.filename, sourceidmap["文档"], doc.id, doc.project_id, project.name)
    MakeMsg(doc, uid, u"编辑")

    return jsonify({}), 200


@api.route('/project/<int:id>/re/', methods=['GET'], endpoint='ProjectReGet')
@login_required(role=1)
def project_re_get(uid, id):

    if not checkid(uid, id):
        return jsonify({}), 401

    docs = Doc.query.filter_by(project_id=id, re=True).all()
    files = File.query.filter_by(project_id=id, re=True).all()

    DocList = []
    FileList = []
    try:
        for doc in docs:
            DocList.append({
                "id": doc.id,
                "name": doc.filename,
                "lastcontent": doc.content[:100]
            })

        for file in files:
            FileList.append({
                "id": file.id,
                "name": file.realname,
                "creator": User.query.filter_by(id=file.creator_id).first().name,
                "url": file.url,
                "create_time": file.create_time,
                "delete_time": file.delete_time
            })
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({
        "FolderList": DocList,
        "FileList": FileList
    }), 200


@api.route('/project/<int:id>/re/', methods=['PUT'], endpoint='ProjectRePut')
@login_required(role=1)
def project_re_put(uid, id):
    if not checkid(uid, id):
        return jsonify({}), 401

    doc_list = request.get_json().get('doc')
    file_list = request.get_json().get('file')

    try:
        for doc_id in doc_list:
            doc = Doc.query.filter_by(id=doc_id).first()
            doc.re = False
            db.session.commit()

        for file_id in file_list:
            file = File.query.filter_by(id=file_id).first()
            file.re = False
            db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({
    }), 200


@api.route('/project/<int:id>/re/', methods=['DELETE'], endpoint='ProjectReDelete')
@login_required(role=1)
def project_re_put(uid, id):
    if not checkid(uid, id):
        return jsonify({}), 401

    doc_list = request.get_json().get('doc')
    file_list = request.get_json().get('file')

    try:
        for doc_id in doc_list:
            doc = Doc.query.filter_by(id=doc_id).first()
            db.session.delete(doc)
        db.session.commit()

        for file_id in file_list:
            file = File.query.filter_by(id=file_id).first()
            ret, info = bucket.delete(bucket_name, file.filename)
            db.session.delete(file)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 404
    return jsonify({
    }), 200
