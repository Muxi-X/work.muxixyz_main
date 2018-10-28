from . import db
from flask import jsonify
from sqlalchemy import desc

def get_rows(Table, Record, Value, pageNum, pageSize, reverse=False):
    print (Record,Value)
    if Record is None:
        rows = db.session.query(Table).count()
    else:
        rows = db.session.query(Table).filter(Record == Value).count()
    pageMax = rows // pageSize
    if rows % pageSize:
        pageMax += 1
    hasNext = True
    if pageNum >= pageMax:
        hasNext = False
    if Record is not None:
        if reverse:
            dataList = db.session.query(Table).filter(Record ==Value).order_by("id desc").limit(pageSize).offset((pageNum-1)*pageSize)
        else:
            dataList = db.session.query(Table).filter(Record == Value).limit(pageSize).offset((pageNum-1)*pageSize)
    else:
        if reverse:
            dataList = db.session.query(Table).order_by("id desc").limit(pageSize).offset((pageNum-1)*pageSize)
        else:
            dataList = db.session.query(Table).limit(pageSize).offset((pageNum-1)*pageSize)
    return {
        'pageNum': pageNum,
        'pageMax': pageMax,
        'hasNext': hasNext,
        'rowsNum': rows,
        'dataList': dataList,
    }
