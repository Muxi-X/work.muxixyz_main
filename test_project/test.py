# copy darren 's code at here
import unittest
import os
from work_muxixyz_app import create_app, db
from flask import current_app, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from work_muxixyz_app.models import Team, Group, User, Project, Message, Statu, File, Comment, User2Project, Folder, File
import random
import json

db = SQLAlchemy()


class BasicTestCase(unittest.TestCase):

    def get_a_api_headers(self, ifToken):
        if ifToken is True:
            return {
                'token': TOKEN,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        else:
            return {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        from work_muxixyz_app.api import api
        self.app.register_blueprint(api, url_prefix='/api/v1.0/')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_management_a_auth(self):
        # muxi=Team(name='test',count=3)
        # superuser=User(name='test1',email='cat@test.com',tel='11111111111',role=7,team_id=1)
        # muxi.creator=1
        # admin=User(name='test2',email='dog@test.com',tel='22222222222',role=1,team_id=1)
        # usr=User(name='test3',email='pig@test.com',tel='33333333333',role=1,team_id=1)
        # project=Project(name='test')
        # rela=User2Project(user_id=6,project_id=6)
        # folder = Folder(name='test', project_id=5)
        file = File(filename='test', kind=1, editor_id=6, creator_id=6, folder_id=1, project_id=5)
        # statu = Statu(content='test', time='test', like=1, comment=1, user_id=5, )
        # db.session.add(muxi)
        # db.session.add(superuser)
        # db.session.add(admin)
        # db.session.add(usr)
        # db.session.add(project)
        # db.session.add(rela)
        # db.session.add(folder)
        db.session.add(file)
        # db.session.add(statu)
        db.session.commit()
        global fid
        fid = str(file.id)
        response = self.client.post(
            url_for('api.login', _external=True),
            data=json.dumps({
                "username": 'test',
            }),
            headers=self.get_a_api_headers(False),
        )
        s = json.loads(response.data.decode('utf-8'))['token']
        global TOKEN
        TOKEN = s

    def test_project_a_1_new(self):
        response = self.client.post(
            url_for('api.project_new', _external=True),
            # 'http://localhost/api/v1.0/project/new/',
            data=json.dumps({
                "username": "test",
                "projectname": "test",
                "userlist": [
                    {
                        "userID": 6,
                        "userName": "test"
                    }
                ],
                "intro": "test"
            }),
            headers=self.get_a_api_headers(True)
        )
        global pid
        pid = json.loads(response.data)['project_id']
        self.assertTrue(response.status_code == 200)

    def test_project_a_2_project(self):
        response = self.client.post(
            url_for('api.project_pid', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            data=json.dumps({
                "intro": "test1",
                "name": "test1"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)


    def test_project_a_3_comments(self):
        response = self.client.post(
            url_for('api.project_file_comments', pid=pid, fid=fid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/1/comments/',
            data=json.dumps({
                "content": "test"
            }),
            headers=self.get_a_api_headers(True)
        )
        global cid
        cid = json.loads(response.data)['cid']
        self.assertTrue(response.status_code == 200)

    def test_project_a_4_member(self):
        response = self.client.put(
            url_for('api.project_member', pid=pid, fid=fid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/member/',
            data=json.dumps({
                "userList": [6]
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_1_comment(self):
        response = self.client.get(
            url_for('api.project_file_comment', pid=pid, fid=fid, cid=cid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comment/' + cid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_2_comments(self):
        response = self.client.get(
            url_for('api.project_file_comments', pid=pid, fid=fid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comments/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_3_member(self):
        response = self.client.get(
            url_for('api.project_member', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/member/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
    #
    def test_project_b_4_project(self):
        response = self.client.get(
            url_for('api.project_pid', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_c_1_comment(self):
        response = self.client.delete(
            url_for('api.project_file_comment', pid=pid, fid=fid, cid=cid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comment/' + cid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_c_2_project(self):
        response = self.client.delete(
            url_for('api.project_pid', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
