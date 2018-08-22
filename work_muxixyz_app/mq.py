import pika
import time


def newfeed(uid, json):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    time1 = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    avatar_url = str(json.avatar_url)
    ACTION = str(json.get('action'))
    KIND = str(json.get('kind'))
    SOURCEID = str(json.get('sourceID'))
    a_feed = time1+'/'+avatar_url+'/'+ACTION+'/'+KIND+'/'+SOURCEID 
    channel.queue_declare(
        queue=str(xid))
    channel.basic_publish(
        exchange='',
        routing_key='feed'),
        body=str(a_feed),
        properties=pika.BasicProperties(
            delivery_mode=2))
    connection.close() 
