import pika
import time


def newfeed(uid, avatar_url, action, kind, sourceID):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    avatar_url = avatar_url
    ACTION = action
    KIND = kind
    SOURCEID = sourceID
    a_feed = {'time':time1,'avatar_url':avatar_url,'action':ACTION,'kind':KIND,'source':SOURCEID 
    channel.queue_declare(
        queue='feed')
    channel.basic_publish(
        exchange='',
        routing_key='feed'),
        body=str(a_feed),
        properties=pika.BasicProperties(
            delivery_mode=2))
    connection.close() 
