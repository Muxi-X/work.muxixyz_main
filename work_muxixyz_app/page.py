from . import db
from flask import jsonify

def get_rows(Table, Record, Value, pageNum, pageSize):
    rows = db.session.query(Table).count()
    pageMax = rows / pageSize + 1
    if rows % pageSize:
        pageMax -= 1
    hasNext = True
    if pageNum >= pageMax:
        hasNext = False
    dataList = db.session.query(Table).filter(Record == Value).limit(pageSize).offset((pageNum-1)*pageSize)

    return {
        'pageNum': pageNum,
        'pageMax': pageMax,
        'hasNext': hasNext,
        'rowsNum': rows,
        'dataList': dataList,
    }
