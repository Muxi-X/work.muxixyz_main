from flask import jsonify, request, current_app, url_for
from . import api
from .. import db
from ..models import Team, Group, User, Project, Message, Statu, File, Folder, Comment, User2Project
from ..decorator import login_required
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config
import os
import requests
from ..mq import newfeed

access_key = 'YCdnGHp2tRa7V0KDisHqXehlny0eVNM5vQow1cQV'  # os.environ.get('ACCESS_KEY)
secret_key = 'ZGgkaNPunh6Y32FcsAtvhOd61rnlcKeeXPZ-qIlr'  # os.environ.get('SECRET_KEY)
url = 'pdw7hnao1.bkt.clouddn.com'                        # os.environ.get('URL')
bucket_name = 'test-work'
q = qiniu.Auth(access_key, secret_key)
bucket = BucketManager(q)

@api.route('project/<int:pid>/folder/<int:foid>/', methods=['POST', 'GET', 'PUT', 'DELETE'], endpoint='ProjectFolder')
@login_required(role = 1)
def project_folder(uid, pid, foid):
    if request.method == 'POST':
        try:
            foldername = request.get_json().get('foldername')
            kind = request.get_json().get('kind')
            if foid != 0:
                folder = Folder(
                    kind=kind,
                    name=foldername,
                    father_id=foid,
                    project_id=pid
                )
            else:
                folder = Folder(
                    kind=kind,
                    name=foldername,
                    father_id=None,
                    project_id=pid
                )
            db.session.add(folder)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "errormessage": str(e)
            }), 500
        action = "create" + folder.name
        kind = 6
        newfeed(uid, action, kind, folder.id)
        return jsonify({
            "foid": str(folder.id)
        }), 201
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
                "errormessage": str(e)
            }), 500
        return jsonify({
            "fList": fList,
            "mList": mList
        }), 200
    elif request.method == 'PUT':
        try:
            foldername = request.get_json().get('foldername')
            folder = Folder.query.filter_by(id=foid, project_id=pid, re=False).first()
            folder.name = foldername
            db.session.add(folder)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "errormessage": str(e)
            }), 500
        action = "revise" + folder.name
        kind = 6
        newfeed(uid, action, kind, folder.id)
        return jsonify({
        }), 200
    elif request.method == 'DELETE':
        name = Folder.query.filter_by(id=foid, re=False).first().name
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
            folder_deleter(foid)
        except Exception as e:
            return jsonify({
                "errormessage": str(e)
            })
        action = "delete" + name
        kind = 6
        newfeed(uid, action, kind, foid)
        return jsonify({
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
                "errormessage": e
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
            return jsonify({
                "errormessage": str(e)
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
                "errormessage": str(e)
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
                "errormessage": str(e)
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
            "errormessage": str(e)
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
                "errormessage": str(e)
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
                "errormessage": str(e)
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
                "errormessage": str(e)
            }), 500
        return jsonify({
            "fList": fList,
            "mList": mList
        })