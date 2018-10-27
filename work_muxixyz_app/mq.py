import pika
from jsoncensor import JsonCensor

import time
import datetime
import os

from work_muxixyz_app import db
from work_muxixyz_app.models import User

MQHOST = os.getenv("WORKBENCH_MQHOST")
MQPORT = 5672
MQUSERNAME = os.getenv("WORKBENCH_MQUSERNAME")
MQPASSWORD = os.getenv("WORKBENCH_MQPASSWORD")
MQQUEUENAME = "feed"

class MessageQueue:

    def __init__(self):
        self.host = MQHOST
        self.port = MQPORT 
        self.username = MQUSERNAME 
        self.password = MQPASSWORD
        self.queuename = MQQUEUENAME
        self.connection = None
        self.channel = None

    def __enter__(self):
        """
        connection and declear
        """
        credentials = pika.PlainCredentials(self.username, self.password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host='/',
                credentials=credentials))
        self.connection = connection
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queuename)
        return self

    def __exit__(self, type, value, traceback):
        """
        close
        """
        self.connection.close()

    def publish(self, body):
        self.channel.basic_publish(
            exchange='',
            routing_key=MQQUEUENAME,
            body=str(body),
            properties=pika.BasicProperties(delivery_mode=2))


def newfeed(uid, action, source_name, source_kind_id, source_object_id, source_project_id=-1, source_project_name="noname"):
    """
    uid: user id
    action: string in [["加入", "创建", "编辑", "删除", "评论", "移动"]]
    source_name: 团队，项目，的名字.文件, 文档，进度的标题.
    source_kind_id: source_list = ["", "团队", "项目", "文档", "文件", "进度"]
    source_object_id: 资源在数据库中的id
    source_project_id: file or doc 所在项目的id
    source_project_name: name

    ***** a feed's structure *****
    {
        "user": {
            "name": string,
            "id": integer,
            "avatar_url": string
        },
        "action": string,
        "source": {
            "kind_id": integer,
            "object_id": integer,
            "project_id": integer, // 没有为-1 
            "name": string
        },
        "time": "2018-10-21-23:15:56" // yyyy-mm-dd-HH:MM:SS  datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S') 
        /* 在返回时扫描&添加
        "split": boolean
        */
    }
    
    """
    user = User.query.filter_by(id=uid).first() or None
    timeday = datetime.datetime.today().strftime('%Y/%m/%d')
    timehm = datetime.datetime.today().strftime('%H:%M')
    a_feed = {
        "user": {
            "name": user.name,
            "id": user.id,
            "avatar_url": user.avatar
        },
        "action": action,
        "source": {
            "kind_id": source_kind_id,
            "object_id": source_object_id,
            "object_name": source_name,
            "project_id": source_project_id,
            "project_name": source_project_name
        },
        "timeday": timeday,
        "timehm": timehm
    }

    if not check_feed(a_feed):
        raise FeedFormatException
    
    with MessageQueue() as q:
        q.publish(a_feed)


def check_feed(feed):
    """
    return: true if ok, false if failed
    """
    feed_example = {
        "user": {
            "name": "string",
            "id": 1,
            "avatar_url": "string"
        },
        "action": "string",
        "source": {
            "kind_id": 1,
            "object_id": 1,
            "project_id": 1,
            "object_name": "string",
            "project_name": "string"
        },
        "timeday": "string",
        "timehm": "string"
    }
    
    jc = JsonCensor(feed_example, feed)
    ret = jc.check()
    return ret['statu']

class FeedFormatException(Exception):
    pass

