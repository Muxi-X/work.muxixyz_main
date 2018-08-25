import os
import time
import requests
from flask import jsonify, request, current_app, url_for, Flask
from . import api
from .. import db
from ..models import Feed, Team, Group, User, User2Project, Message, Statu, File, Comment, Project
from ..decorator import login_required
from work_muxixyz_app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from ..mq import newfeed


#KIND = ['Statu', 'Project', 'Doc', 'Comment', 'Team', 'User', 'File']
num = 0
page = 1

@api.route('/status/new/', methods=['POST'], endpoint='newstatus')
@login_required(1)
def newstatus(uid):
    content = request.get_json().get('content')
    title = request.get_json().get('title')
    time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    statu = Statu(
        content=content,
        title=title,
        time=time1,
        like=0,
        comment=0,
        user_id=uid)
    db.session.add(statu)
    db.session.commit()
    user = User.query.filter_by(id=uid).first()
    avatar_url = user.avatar
    action = 'update '+ user.name + '\'s status'
    kind = 0
    sourceID = 0
    newfeed(
        uid,
        avatar_url,
        action,
        kind,
        sourceID)
    response = jsonify({"message":"feed add successfully"})
    response.status_code = 200
    return response


@api.route('/status/<int:sid>/', methods=['GET'], endpoint='getstatu')
@login_required(1)
def getstatu(uid,sid):
    statu = Statu.query.filter_by(id=sid).first()
    title = statu.title
    content = statu.content
    time = statu.time
    likeCount = statu.like
    commentCount = statu.comment
    user =  User.query.filter_by(id=uid).first()
    username = user.name
    avatar = user.avatar
    comments = Comment.query.filter_by(statu_id=sid).all()
    commentList = []
    a_comment = {}
    for comment in comments:
        user_c = User.query.filter_by(id=comment.creator).first()
        a_comment['username'] = user_c.name
        a_comment['avatar'] = user_c.avatar
        a_comment['time'] = comment.time
        a_comment['content'] =  comment.content
        commentList.append(a_comment)
    response = jsonify({
        "title": title,
        "content": content,
        "avatar": avatar,
        "time": time,
        "likeCount": likeCount,
        "commentCount": commentCount,
        "userID": uid,
        "username": username,
        "commentList": commentList})
    response.status_code = 200
    return response


@api.route('/status/<int:sid>/', methods=['DELETE'], endpoint='deletestatu')
@login_required(1)
def deletestatu(uid,sid):
    if Statu.query.filter_by(id=sid).first() is not None:
        Statu.query.filter_by(id=sid).delete()
        response = jsonify({"message":"already delete the statu"})
    else:
        response = jsonify({"message":"the statu has already been deleted"})
    response.status_code = 200
    return response


@api.route('/status/list/<int:page>/', methods=['GET'], endpoint='statulist')
@login_required(1)
def statulist(uid, page):
    status = Statu.query.all()
    statuList = []
    a_statu = {}
    for statu in status:
        global num
        num += 1
        if num > (page-1)*20 and num <= page*20:
            user = User.query.filter_by(id=statu.user_id).first()
            a_statu['username'] = user.name
            a_statu['time'] = statu.time
            a_statu['avatar'] = user.avatar
            a_statu['title'] = statu.title
            a_statu['content'] = statu.content
            a_statu['likeCount'] = statu.like
            a_statu['commentCount'] = statu.comment
            statuList.append(a_statu)
    response = jsonify({
        "statuList": statuList,
        "page": page})
    response.status_code = 200
    return response


@api.route('/status/<int:userid>/list/<int:page>/', methods=['GET'], endpoint='user_statulist')
@login_required(1)
def user_statulist(uid, userid, page):
    status = Statu.query.filter_by(user_id=userid).all()
    statuList = []
    a_statu = {}
    for statu in status:
        global num
        num += 1
        if num > (page-1)*20 and num <= page*20:
            a_statu['time'] = statu.time
            a_statu['content'] = statu.content
            a_statu['likeCount'] = statu.like
            a_statu['commentCount'] = statu.comment
            statuList.append(a_statu)
    response = jsonify({
        "statuList": statuList,
        "page": page})
    response.status_code = 200
    return response



@api.route('/status/<int:sid>/comments/', methods=['POST'], endpoint='newcomments')
@login_required(1)
def newcomments(uid, sid):
    content = request.get_json().get('content')
    time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    comment = Comment(
        content=content,
        time=time1,
        kind = 0,
        creator = uid,
        file_id = 1,
        statu_id = sid)
    db.session.add(comment)
    db.session.commit()
    user = User.query.filter_by(id=uid).first()
    avatar_url = user.avatar
    action = 'comment '+ user.name + '\'s status'
    kind = 3
    sourceID = db.session.query(func.max(Comment.id)).one()
    sourceID = sourceID[0]
    newfeed(
        uid,
        avatar_url,
        action,
        kind,
        sourceID)
    response = jsonify({"message":"feed add successfully"})
    response.status_code = 200
    return response


@api.route('/status/<int:sid>/comment/<int:cid>/', methods=['GET'], endpoint='getcomment')
@login_required(1)
def getcomment(uid, sid, cid):
    comment = Comment.query.filter_by(id=cid).first()
    if comment is not None:
        user = User.query.filter_by(id=comment.creator).first()
        username = user.name
        time1 = comment.time
        avatar = user.avatar
        content = comment.content
        response = jsonify({
            "username": username,
            "avatar": avatar,
            "time": time1,
            "content": content})
        response.status_code = 200
    else:
        response = jsonify({"message": "can't find comment"})
        response.status_code = 402
    return response


@api.route('/status/<int:sid>/comment/<int:cid>/', methods=['DELETE'], endpoint='deletecomment')
@login_required(1)
def deletecomment(uid, sid, cid):
    if Comment.query.filter_by(id=cid).first() is not None:
        Comment.query.filter_by(id=cid).delete()
        response = jsonify({"message":"ok"})
        response.status_code = 200
    else:
        response = jsonify({"message":"can't find"})
        response.status_code = 402 
    return response


@api.route('/status/<int:sid>/comments/', methods=['GET'], endpoint='getcommentlist')
@login_required(1)
def getcommentlist(uid, sid):
    comments = Comment.query.filter_by(statu_id=sid).all()
    if comments is not None:
        a_comment = {}
        commentlist = []
        for comment in comments:
            user = User.query.filter_by(id=comment.creator).first()
            a_comment['username'] = user.name
            a_comment['avatar'] = user.avatar
            a_comment['time'] = comment.time
            a_comment['comment'] = comment.content
            commentlist.append(a_comment)
        response = jsonify({
                "commentList": commentlist})
        response.status_code = 200
    else:
        response = jsonify({"message": "can't find"})
        response.status_code = 402
    return response


