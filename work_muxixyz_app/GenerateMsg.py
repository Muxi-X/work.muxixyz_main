import time
from . import db
from .timetools import to_readable_time as TRT
from flask import jsonify
from flask import abort,request
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
        usrs=User2File.query.filter_by(file_kind = self.kind, file_id = self._include.id).all()
        return usrs
    

def MakeMsg(obj, Driver, action):
    f__k = Foolish(obj)
    users = f__k.getAttentionList()
    if users is None:
        return True
    for user in users:
        msg = Message(  time = TRT(time.time()),
                        action = action,
                        from_id = Driver,
                        receive_id = user.id,
                        file_kind = f__k.kind,
                        file_id = obj.id)
        db.session.add(msg)
    db.session.commit()
    return True