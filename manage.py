import sys
import importlib
import os
import time
import pika
from work_muxixyz_app import create_app, db
from work_muxixyz_app.models import Team,Group,User,Project,Message,Statu,File,Comment,Doc
from work_muxixyz_app.models import Feed
from flask_script import Manager,Shell,Command
from flask_migrate import Migrate,MigrateCommand
from sqlalchemy import func

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
manager=Manager(app)
migrate=Migrate(app,db)

manager.add_command('db',MigrateCommand)

MQHOST = os.getenv('MQHOST') or '120.78.194.125'
MQUSERNAME = os.getenv("MQUSERNAME")
MQPASSWORD = os.getenv("MQPASSWORD")



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
def test_message():

    import unittest
    tests=unittest.TestLoader().discover('test_message')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def createdb():
    db.create_all()

if __name__=='__main__':
    manager.run()
    app.run(debug=True)
