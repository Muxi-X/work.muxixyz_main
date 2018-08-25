import sys
import importlib
import os
import time
import pika
from work_muxixyz_app import create_app,db
from work_muxixyz_app.models import Team,Group,User,Project,Message,Statu,File,Comment,Feed
from flask_script import Manager,Shell,Command
from flask_migrate import Migrate,MigrateCommand
from sqlalchemy import func


importlib.reload(sys)
#export PYTHONIOENCODING="UTF-8"

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)
migrate=Migrate(app,db)

manager.add_command('db',MigrateCommand)

MQHOST = os.getenv('MQHOST') or 'localhost'

def make_shell_context():
    return dict(app=app)

manager.add_command("shell",Shell(make_context=make_shell_context))

@manager.command
def test_management():

    import unittest
    tests=unittest.TestLoader().discover('test_management')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def test_project():

    import unittest
    tests=unittest.TestLoader().discover('test_project')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def test_status():
    import unittest
    tests = unittest.TestLoader().discover('test_status')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def receive():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=MQHOST))
    channel = connection.channel()
    feed_queue = channel.queue_declare(queue='feed')
    def callback(ch, method, properties, body):
        feed = eval(body.decode())
        lastestid = db.session.query(func.max(Feed.id))
        last_feed = Feed.query.filter_by(id=lastestid).first()
        if last_feed == None:
            feed['divider'] = True
        elif last_feed.kind == feed['kind']:
            feed['divider'] = False
        else:
            feed['divider'] = True
        feed = Feed(
            time=feed['time'],
            avatar_url=feed['avatar_url'],
            user_id=feed['uid'],
            action=feed['action'],
            kind=feed['kind'],
            sourceid=feed['sourceid'],
            divider=feed['divider'])
        db.session.add(feed)
        db.session.commit()
    channel.basic_consume(
        callback,
        queue='feed',
        no_ack=True)
    channel.start_consuming()


@manager.command
def createdb():
    db.create_all()

if __name__=='__main__':
    manager.run()
    app.run(debug=True)
