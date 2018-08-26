import pika
import time
import os
from work_muxixyz_app import db
from work_muxixyz_app.models import User

MQHOST = os.getenv("MQHOST") or "120.78.194.125"
MQUSERNAME = os.getenv("MQUSERNAME") or "feed"
MQPASSWORD = os.getenv("MQPASSWORD") or "muxixyz"

def newfeed(uid, action, kind, sourceID):
    credentials = pika.PlainCredentials(MQUSERNAME, MQPASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=MQHOST,
            port=5672,
            virtual_host='/',
            credentials=credentials))
    channel = connection.channel()
    time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    user = User.query.filter_by(id=uid).first()
    username = user.name
    avatar_url = user.avatar
    ACTION = username + ' ' + action
    KIND = kind
    SOURCEID = sourceID
    a_feed = {
        'time':time1,
        'avatar_url':avatar_url,
        'uid':uid,
        'action':ACTION,
        'kind':KIND,
        'sourceid':SOURCEID}
    channel.queue_declare(queue='feed')
    channel.basic_publish(
        exchange='',
        routing_key='feed',
        body=str(a_feed),
        properties=pika.BasicProperties(
            delivery_mode=2))
    connection.close()
