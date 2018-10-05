# -*- coding: UTF-8 -*-

from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Team, Group, User, Project, Message, Statu, File, Doc, FolderForFile, FolderForMd, Comment, \
    User2Project
from ..decorator import login_required
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
import os
import requests
import time
from ..mq import newfeed
from werkzeug import secure_filename

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


@api.route('/folder/file/', methods=['POST'], endpoint='FolderFilePost')
@login_required(role=1)
def folder_file_post(uid):
    try:
        foldername = request.get_json().get('foldername')
        project_id = request.get_json().get('project_id')

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
    newfeed(uid, u"创建" + folderforfile.name, 6, folderforfile.id)
    return jsonify({
        "id": str(folderforfile.id)
    }), 201


@api.route('/folder/file/<int:id>/', methods=['PUT'], endpoint='FolderFileIdPut')
@login_required(role=1)
def folder_file_id_put(uid, id):
    try:
        foldername = request.get_json().get('foldername')
        folderforfile = FolderForFile.query.filter_by(id=id).first()
        folderforfile.name = foldername
        db.session.add(folderforfile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, u"编辑" + folderforfile.name, 6, folderforfile.id)
    return jsonify({}), 200


@api.route('/folder/file/<int:id>/', methods=['DELETE'], endpoint='FolderFileIdDelete')
@login_required(role=1)
def folder_file_id_delete(uid, id):
    name = FolderForFile.query.filter_by(id=id).first().name

    folder = request.get_json().get('folder')
    file = request.get_json().get('file')

    try:
        for folder_id in folder:
            folderforfile = FolderForFile.query.filter_by(id=folder_id).first()
            folderforfile.re = True
            # db.session.delete(folderforfile)
        db.session.commit()

        for file_id in file:
            file = File.query.filter_by(id=file_id).first()
            # ret, info = bucket.delete(bucket_name, file.filename)         # 用于彻底删除，但是这里应该只是移动到回收站
            file.re = True
        db.session.commit()

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    newfeed(uid, u"删除" + name, 6, id)
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
            FolderList.append({
                "id": folderforfile.id,
                "name": folderforfile.name
            })

        for file_id in file_list:
            file = File.query.filter_by(id=file_id).first()
            FileList.append({
                "id": file.id,
                "name": file.realname,
                "creator": User.query.filter_by(id=uid).first().name,
                "url": file.url,
                "create_time": file.create_time
            })
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
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
        }), 500
    newfeed(uid, u"创建" + folderformd.name, 6, folderformd.id)
    return jsonify({
        "id": str(folderformd.id)
    }), 201


@api.route('/folder/doc/<int:id>/', methods=['PUT'], endpoint='FolderDocIdPut')
@login_required(role=1)
def folder_doc_id_put(uid, id):
    try:
        foldername = request.get_json().get('foldername')
        folderformd = FolderForMd.query.filter_by(id=id).first()
        folderformd.name = foldername
        db.session.add(folderformd)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, u"编辑" + folderformd.name, 6, folderformd.id)
    return jsonify({}), 200


@api.route('/folder/doc/<int:id>/', methods=['DELETE'], endpoint='FolderDocIdDelete')
@login_required(role=1)
def folder_doc_id_delete(uid, id):
    name = FolderForMd.query.filter_by(id=id).first().name

    folder = request.get_json().get('folder')
    doc = request.get_json().get('doc')

    try:
        for folder_id in folder:
            folderformd = FolderForMd.query.filter_by(id=folder_id).first()
            folderformd.re = True
            # db.session.delete(folderforfile)
        db.session.commit()

        for doc_id in doc:
            doc = Doc.query.filter_by(id=doc_id).first()
            # ret, info = bucket.delete(bucket_name, doc.filename)         # 用于彻底删除，但是这里应该只是移动到回收站
            doc.re = True
        db.session.commit()

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    newfeed(uid, u"删除" + name, 6, id)
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
            FolderList.append({
                "id": folderformd.id,
                "name": folderformd.name
            })

        for doc_id in doc_list:
            doc = Doc.query.filter_by(id=doc_id).first()
            DocList.append({
                "id": doc.id,
                "name": doc.filename,
                "lastcontent": doc.content[:100]
            })
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    return jsonify({
        "FolderList": FolderList,
        "DocList": DocList
    }), 200


@api.route('/file/file/', methods=['POST'], endpoint='FileFilePost')
@login_required(role=1)
def file_file_post(uid):
    myfile = request.files.get('file')
    project_id = request.form.get('project_id')
    try:
        filename = secure_filename(myfile.filename) + str(time.time())[-4:]
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
        }), 500
    newfeed(uid, u"创建" + myfile.filename, 6, newfile.id)
    return jsonify({
        "fid": str(newfile.id),
        "name": myfile.filename
    }), 201


@api.route('/file/file/<int:id>/', methods=['DELETE'], endpoint='FileFileIdDelete')
@login_required(role=2)
def file_file_id_delete(uid, id):
    try:
        file = File.query.filter_by(id=id).first()
        file.re = True
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    newfeed(uid, u"删除" + file.filename, 6, file.id)
    return jsonify({}), 200


@api.route('/file/doc/', methods=['POST'], endpoint='FileDocPost')
@login_required(role=1)
def file_doc_post(uid):
    mdname = request.get_json().get('mdname')
    mycontent = request.get_json().get('content')
    project_id = request.get_json().get('project_id')
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
        newfeed(uid, u"创建" + mdname, 6, newdoc.id)
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 500
    return jsonify({
        "fid": str(newdoc.id)
    }), 201


@api.route('/file/doc/<int:id>/', methods=['DELETE'], endpoint='FileDocIdDelete')
@login_required(role=2)
def file_doc_id_delete(uid, id):
    try:
        doc = Doc.query.filter_by(id=id).first()
        doc.re = True
        db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    newfeed(uid, u"删除" + doc.filename, 6, doc.id)
    return jsonify({}), 200


@api.route('/file/doc/<int:id>/', methods=['GET'], endpoint='FileDocIdGet')
@login_required(role=1)
def file_doc_id_get(uid, id):
    doc = Doc.query.filter_by(id=id).first()
    try:
        return jsonify({
            "name": doc.filename,
            "creator": User.query.filter_by(id=doc.creator_id).first().name,
            "conetnt": doc.content,
            "lasteditor": User.query.filter_by(id=doc.editor_id).first().name,
            "create_time": doc.create_time,
        }), 200
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500


@api.route('/file/doc/<int:id>/', methods=['PUT'], endpoint='FileDocIdPut')
@login_required(role=1)
def file_doc_id_put(uid, id):
    doc = Doc.query.filter_by(id=id).first()
    DocName = request.get_json().get('DocName')
    content = request.get_json().get('content')
    try:
        doc.filename = DocName
        doc.content = content
        db.session.commit()
    except Exception as e:
        return jsonify({
            'errmsg': str(e)
        })
    newfeed(uid, u"编辑" + doc.filename, 6, doc.id)
    return jsonify({}), 200


@api.route('/project/re/', methods=['GET'], endpoint='ProjectReGet')
@login_required(role=1)
def project_re_get(uid):
    id = request.get_json().get('id')

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
                "name": file.filename,
                "creator": User.query.filter_by(id=uid).first().name,
                "url": file.url,
                "create_time": file.create_time
            })
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    return jsonify({
        "FolderList": DocList,
        "FileList": FileList
    }), 200


@api.route('/project/re/', methods=['PUT'], endpoint='ProjectRePut')
@login_required(role=1)
def project_re_put(uid):
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
        })
    return jsonify({
    }), 200


@api.route('/project/re/', methods=['DELETE'], endpoint='ProjectReDelete')
@login_required(role=1)
def project_re_put(uid):
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
        })
    return jsonify({
    }), 200
