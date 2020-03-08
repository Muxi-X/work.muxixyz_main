import time
from . import db
from .timetools import to_readable_time as TRT
from flask import jsonify
from flask import abort, request
from flask import current_app
from .models import User, Message, File, Doc, Statu, User2File, Project, Team, Group

class Foolish(object):
    cls = None
    kind = None

    def __init__(self, obj):
        self._include = obj
        self._ClsName = obj.__tablename__
        if 'doc' in self._ClsName:
            self.cls = Doc
            self.kind = 0
        if 'file' in self._ClsName:
            self.cls = File
            self.kind = 1
    
    def getAttentionList(self):
        usrs = list([x.user_id] for x in User2File.query.filter_by(file_kind = self.kind, file_id = self._include.id).all() )
        return usrs

# params:
#   obj:    (file_mode)File or Doc; (comment_mode)Statu;
#   Driver: (file_mode)UserID;      (comment_mode)UserID;
#   action: (file_mode)actionString;(comment_mode)actionString;
#   is_comment: (file_mode)False;   (comment_mode)True;
def MakeMsg(obj, Driver, action, is_comment=False):
    # ShiinaOrez at 2020-03-09; NewFeature at 工作台迭代(李纪欣)
    # 评论产生的消息的逻辑
    # message中的file_id为进度的ID
    if is_comment:
        if obj is None or action == "":
            return True
        msg = Message(  time = TRT(time.time())),
                        action = action,
                        from_id = Driver,
                        receive_id = obj.user_id,
                        file_kind = 2,
                        file_id = obj.id)
        db.session.add(msg)
        db.session.commit()
        return True

    # 文件正常产生消息的逻辑
    f__k = Foolish(obj)
    users = f__k.getAttentionList()
    if users is None:
        return True
    for user in f__k.getAttentionList():
        msg = Message(  time = TRT(time.time()),
                        action = action,
                        from_id = Driver,
                        receive_id = user,
                        file_kind = f__k.kind,
                        file_id = obj.id)
        db.session.add(msg)
    db.session.commit()
    return True
