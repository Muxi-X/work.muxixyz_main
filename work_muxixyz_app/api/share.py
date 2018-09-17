import os
import time
import requests
import base64
from flask import jsonify, request, current_app, url_for, Flask
from . import api
from .. import db
from ..models import User, File, Comment, Doc
from ..decorator import login_required
from work_muxixyz_app import db
from flask_sqlalchemy import SQLAlchemy
from qiniu import Auth, put_file, etag, BucketManager
import qiniu.config

access_key = os.environ.get('WORKBENCH_ACCESS_KEY')
secret_key = os.environ.get('WORKBENCH_SECRET_KEY')
url = os.environ.get('WORKBENCH_URL')
bucket_name = 'test-work'
q = qiniu.Auth(access_key, secret_key)
bucket = BucketManager(q)


@api.route('/share/<int:docid>/', methods=["GET"], endpoint='sharedoc')
@login_required(1)
def sharedoc(uid, docid):
    data = {
        "uid": uid,
        "docid": docid
    }
    data = str(data)
    bytestr = data.encode(encoding='utf-8')
    b64url = base64.b64encode(bytestr)
    response = jsonify({"url": str(b64url)})
    response.status_code = 200
    return response


@api.route('/share/viewdoc/<url>/', methods=["GET"], endpoint='viewdoc')
def viewdoc(url):
    url = eval(url)
    url = url.get('url')
    url = eval(url)
    url = base64.b64decode(url)
    url = url.decode()
    data = eval(url)
    docid = data.get('docid')
    doc = File.query.filter_by(id=docid).first()
    docname = doc.filename
    finaleditor = User.query.filter_by(id=doc.editor_id).first().name
    creator = User.query.filter_by(id=doc.creator_id).first().name
    base_url = doc.url
    private_url = q.private_download_url(base_url, expires=3600)
    r = requests.get(private_url)
    content = r.text
    response = jsonify({
        "title":docname,
        "content":content,
        "finaleditor":finaleditor,
        "creator":creator})
    response.status_code = 200
    return response
