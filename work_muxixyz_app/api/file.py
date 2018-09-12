# -*- coding: UTF-8 -*-

from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Team, Group, User, Project, Message, Statu, File, Doc , FolderForFile, FolderForMd, Comment, User2Project
from ..decorator import login_required
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
import os
import requests
import time
from ..mq import newfeed

access_key = app.config['ACCESS_KEY']
secret_key = app.config['SECRET_KEY']
url = app.config['URL']
bucket_name = 'test-work'
q = qiniu.Auth(access_key, secret_key)
bucket = BucketManager(q)


@api.route('/folder/file/', methods=['POST'], endpoint='FolderFilePost')
@login_required(role = 1)
def folder_file_post(uid):
    try:
        foldername = request.get_json().get('foldername')
        project_id = request.get_json().get('project_id')

        folderforfile = FolderForFile(
            name=foldername,
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            create_id = uid,
            project_id=pid
        )
        db.session.add(folderforfile)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, "create" + folderforfile.name, 6, folder.id)
    return jsonify({
        "id": str(folderforfile.id)
    }), 201


@api.route('/folder/file/<int:id>/', methods=['PUT'], endpoint='FolderFileIdPut')
@login_required(role = 1)
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
    newfeed(uid, "revise" + folderforfile.name, 6, folder.id)
    return jsonify({}), 200


@api.route('/folder/file/<int:id>/', methods=['DELETE'], endpoint='FolderFileIdDelete')
@login_required(role = 1)
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
            # db.session.delete(file)
        db.session.commit()

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    newfeed(uid, "delete" + name, 6, id)
    return jsonify({}), 200


@api.route('/folder/file/children/', methods=['POST'], endpoint='FolderFileChrildrenPost')
@login_required(role = 1)
def folder_file_chrildren_post(uid):
    folder = request.get_json().get('folder')
    file = request.get_json().get('file')

    FolderList = []
    FileList = []
    try:
        for folder_id in folder:
            folderforfile = FolderForFile.query.filter_by(id=folder_id).first()
            FolderList.append({
                "id": folderforfile.id,
                "name": folderforfile.name
            })

        for file_id in file:
            file = File.query.filter_by(id=file_id).first()
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
        "FolderList": FolderList,
        "FileList": FileList
    }), 200


@api.route('/folder/doc/', methods=['POST'], endpoint='FolderDocPost')
@login_required(role = 1)
def folder_doc_post(uid):
    try:
        foldername = request.get_json().get('foldername')
        project_id = request.get_json().get('project_id')

        folderformd = FolderForMd(
            name=foldername,
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            create_id = uid,
            project_id=pid
        )
        db.session.add(folderformd)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "errmsg": str(e)
        }), 500
    newfeed(uid, "create" + folderformd.name, 6, folder.id)
    return jsonify({
        "id": str(folderformd.id)
    }), 201


@api.route('/folder/doc/<int:id>/', methods=['PUT'], endpoint='FolderDocIdPut')
@login_required(role = 1)
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
    newfeed(uid, "revise" + folderformd.name, 6, folder.id)
    return jsonify({}), 200


@api.route('/folder/doc/<int:id>/', methods=['DELETE'], endpoint='FolderDocIdDelete')
@login_required(role = 1)
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
            # ret, info = bucket.delete(bucket_name, file.filename)         # 用于彻底删除，但是这里应该只是移动到回收站
            doc.re = True
            # db.session.delete(file)
        db.session.commit()

    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        })
    newfeed(uid, "delete" + name, 6, id)
    return jsonify({}), 200


@api.route('/folder/doc/children/', methods=['POST'], endpoint='FolderDocChrildrenPost')
@login_required(role = 1)
def folder_doc_chrildren_post(uid):
    folder = request.get_json().get('folder')
    doc = request.get_json().get('doc')

    FolderList = []
    DocList = []
    try:
        for folder_id in folder:
            folderformd = FolderForMd.query.filter_by(id=folder_id).first()
            FolderList.append({
                "id": folderformd.id,
                "name": folderformd.name
            })

        for doc_id in doc:
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
    file = request.files.get('file')
    project_id = request.get_json().get('project_id')
    try:
        file.save(os.path.join(os.getcwd(), file.filename).encode('utf-8').strip())
        filename = file.filename
        key = filename
        localfile = os.path.join(os.getcwd(), file.filename)
        res = qiniu_upload(key, localfile)
        i = res.find('com')
        res = 'http://' + res[:i+3] + '/' + res[i+3:]
        os.remove(localfile)
        newfile = File(
            url=res,
            filename=filename,
            create_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            create_id=uid,
            project_id=project_id,
        )
        db.session.add(newfile)
        db.session.commit()
    except Exception as e:
            db.session.rollback()
            return jsonify({
                "errmsg": str(e)
            }), 500
    newfeed(uid, "create" + filename, 6, newfile.id)
    return jsonify({
        "fid": str(newfile.id)
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
    newfeed(uid, "delete" + file.filename, 6, newfile.id)
    return jsonify({}), 200


@api.route('/file/doc/', methods=['POST'], endpoint='FileDocPost')
@login_required(role=1)
def file_doc_post(uid):
    mdname = request.get_json().get('mdname')
    content = request.get_json().get('content')
    project_id = request.get_json().get('project_id')
    try:
        newdoc = Doc(
            content=content,
            filename=mdname,
            create_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            create_id=uid,
            editor_id=uid,
            project_id=project_id,
        )
        db.session.add(newdoc)
        db.session.commit()
    except Exception as e:
            db.session.rollback()
            return jsonify({
                "errmsg": str(e)
            }), 500
    newfeed(uid, "create" + mdname, 6, newdoc.id)
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
    newfeed(uid, "delete" + doc.filename, 6, newdoc.id)
    return jsonify({}), 200


@api.route('/file/doc/<int:id>/', methods=['GET'], endpoint='FileDocIdGet')
@login_required(role=1)
def file_doc_id_get(uid, id):
    doc = Doc.query.filter_by(id=id).first()
    try:
        return jsonify({
            "name": doc.filename,
            "creator": User.query.filter_by(id=doc.create_id).first().name,
            "conetnt": doc.content,
            "lasteditor": User.query.filter_by(id=doc.editor_id).first().name,
            "create_time": doc.create_time,
         }),200
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
    newfeed(uid, "update" + doc.filename, 6, newdoc.id)
    return jsonify({}), 200

    elif request.method == 'GET':
        fList = []
        mList = []
        try:
            files = File.query.filter_by(folder_id=foid, project_id=pid, re=False).all()
            folders = Folder.query.filter_by(father_id=foid, project_id=pid, re=False).all()
            for fi in files:
                did = fi.id
                dname = fi.filename
                if fi.kind == False:
                    fList.append({
                        "kind": 1,
                        "id": did,
                        "name": dname
                    })
                else:
                    mList.append({
                        "kind": 1,
                        "id": did,
                        "name": dname
                    })
            for fo in folders:
                mid = fo.id
                mname = fo.name
                if fo.kind == False:
                    fList.append({
                        "kind": 2,
                        "id": mid,
                        "name": mname
                    })
                else:
                    mList.append({
                        "kind": 2,
                        "id": mid,
                        "name": mname
                    })
        except Exception as e:
            return jsonify({
                "errmsg": str(e)
            }), 500
        return jsonify({
            "fList": fList,
            "mList": mList
        }), 200


@api.route('froject/<int:pid>/file/<int:foid>/<int:fid>/', methods=['POST', 'GET', 'PUT', 'DELETE'], endpoint='ProjectFile')
@login_required(role = 1)
def project_file(uid, pid, foid, fid):

    def qiniu_upload(key, localfile):
        token = q.upload_token(bucket_name, key, 3600)

        ret, info = qiniu.put_file(token, key, localfile)

        if ret:
            return '{0}{1}'.format(url, ret['key'])
        else:
            raise UploadError('上传失败，请重试')
    if request.method == 'POST':
        kind = request.get_json().get('kind')
        try:
            if kind == False:
                file = request.files['file']
                file.save(os.path.join(os.getcwd(), file.filename).encode('utf-8').strip())
                filename = request.get_json().get('filename') + file.filename.split('.')[1]
                key = filename
                localfile = os.path.join(os.getcwd(), file.filename)
                res = qiniu_upload(key, localfile)
                i = res.find('com')
                res = 'http://' + res[:i+3] + '/' + res[i+3:]
                os.remove(localfile)
            else:
                filename = request.get_json().get('filename') + '.md'
                content = request.get_json().get('content')
                file = open(os.getcwd() + '/' + filename, 'w')
                file.writelines(content)
                file.close()
                key = filename
                localfile = os.getcwd() + '/' + filename
                res = qiniu_upload(key, localfile)
                i = res.find('com')
                res = 'http://' + res[:i+3] + '/' + res[i+3:]
                os.remove(localfile)
            myfile = File(
                url=res,
                filename=filename,
                kind=kind,
                editor_id=uid,
                creator_id=uid,
                folder_id=foid,
                project_id=pid
            )
            db.session.add(myfile)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "errmsg": e
            }), 500
        action = "create" + myfile.filename
        kind = 6
        newfeed(uid, action, kind, myfile.id)
        return jsonify({
            "fid": str(myfile.id)
        }), 201
    elif request.method == 'GET':
        try:
            file = File.query.filter_by(id=fid, re=False).first()
            name = file.filename
            finalleditor = User.query.filter_by(id=file.editor_id).first().name
            creator = User.query.filter_by(id=file.creator_id).first().name
            base_url = file.url
            kind = file.kind
            if kind == True:
                private_url = q.private_download_url(base_url, expires=3600)
                r = requests.get(private_url)
                content = r.text
            else:
                content = ' '
        except Exception as e:
            print(e)
            return jsonify({
                "errmsg": str(e)
            }), 500
        return jsonify({
            "name": name,
            "content": content,
            "finalleditor": finalleditor,
            "creator": creator,
            "url": base_url,
            "kind": kind
        }), 200
    elif request.method == 'PUT':
        try:
            file = File.query.filter_by(id=fid, re=False).first()
            de = file.filename
            filename = request.get_json().get('filename')
            content = request.get_json().get('content')
            f = open(os.getcwd() + '/' + filename + '.md', 'w')
            f.writelines(content)
            f.close()
            key = filename + '.md'
            localfile = os.getcwd() + '/' + filename + '.md'
            res = qiniu_upload(key, localfile)
            i = res.find('com')
            res = 'http://' + res[:i+3] + '/' + res[i+3:]
            os.remove(localfile)
            ret, info = bucket.delete(bucket_name, de)
            file.filename = filename + '.md'
            file.url = res
            file.editor_id = uid
            db.session.add(file)
            db.session.commit()
        except Exception as e:
            return jsonify({
                "errmsg": str(e)
            }), 500
        action = "revise" + file.filename
        kind = 6
        newfeed(uid, action, kind, file.id)
        return jsonify({
        }), 200
    elif request.method == 'DELETE':
        try:
            file = File.query.filter_by(id=fid, re=False).first()
            if file.creator_id != uid:
                return jsonify({}), 401
            ret, info = bucket.delete(bucket_name, file.filename)
            db.session.delete(file)
            db.session.commit()
        except Exception as e:
            return jsonify({
                "errmsg": str(e)
            }), 500
        action = "delete" + file.filename
        kind = 6
        newfeed(uid, action, kind, file.id)
        return jsonify({
        }), 200
    else:
        return jsonify({
        }), 403


@api.route('project/<int:pid>/f<int:foid>/<int:toid>/', methods=['PUT'], endpoint='ProjectF')
@login_required(role = 1)
def project_f(uid, pid, foid, toid):
    kind = request.get_json().get('kind')
    try:
        if kind == 1:
            folder = Folder.query.filter_by(id=foid, re=False).first()
            folder.father_id = toid
            mid = folder.id
            mname = folder.name
            db.session.add(folder)
            db.session.commit()
        else:
            file = File.query.filter_by(id=foid, re=False).first()
            file.folder_id = toid
            mid = file.id
            mname = file.filename
            db.session.add(file)
            db.session.commit()
    except Exception as e:
        return jsonify({
            "errmsg": str(e)
        }), 500
    action = "move" + mname
    kind = 6
    newfeed(uid, action, kind, mid)
    return jsonify({
    }), 200


@api.route('project/<int:pid>/re/',  methods=['POST', 'GET', 'PUT'], endpoint='ProjectRe')
@login_required(role = 1)
def project_re(uid, pid):
    if request.method == 'POST':
        id = request.get_json().get("id")
        kind = request.get_json().get("kind")
        try:
            if kind == 1:
                file = File.query.filter_by(id=id).first()
                file.re = True
                mid = file.id
                mname = file.filename
                db.session.add(file)
                db.session.commit()
            else:
                folder = Folder.query.filter_by(id=id).first()
                folder.re = True
                mid = folder.id
                mname = folder.name
                db.session.add(folder)
                db.session.commit()
        except Exception as e:
            return jsonify({
                "errmsg": str(e)
            }), 500
        action = "delete" + mname
        kind = 6
        newfeed(uid, action, kind, mid)
        return jsonify({
        }), 200
    elif request.method == 'PUT':
        id = request.get_json().get("id")
        kind = request.get_json().get("kind")
        try:
            if kind == 1:
                file = File.query.filter_by(id=id).first()
                file.re = False
                mid = file.id
                mname = file.filename
                db.session.add(file)
                db.session.commit()
            else:
                folder = Folder.query.filter_by(id=id).first()
                folder.re = False
                mid = folder.id
                mname = folder.name
                db.session.add(folder)
                db.session.commit()
        except Exception as e:
            return jsonify({
                "errmsg": str(e)
            }), 500
        action = "put back" + mname
        kind = 6
        newfeed(uid, action, kind, mid)
        return jsonify({
        }), 200
    elif request.method == 'GET':
        fList = []
        mList = []
        try:
            files = File.query.filter_by(re=True).all()
            folders = Folder.query.filter_by(re=True).all()
            for fi in files:
                did = fi.id
                dname = fi.filename
                if fi.kind == False:
                    fList.append({
                        "kind": 1,
                        "id": did,
                        "name": dname
                    })
                else:
                    mList.append({
                        "kind": 1,
                        "id": did,
                        "name": dname
                    })
            for fo in folders:
                mid = fo.id
                mname = fo.name
                if fo.kind == False:
                    fList.append({
                        "kind": 2,
                        "id": mid,
                        "name": mname
                    })
                else:
                    mList.append({
                        "kind": 2,
                        "id": mid,
                        "name": mname
                    })
        except Exception as e:
            return jsonify({
                "errmsg": str(e)
            }), 500
        return jsonify({
            "fList": fList,
            "mList": mList
        })
