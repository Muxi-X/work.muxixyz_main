# copy darren 's code at here
import unittest
import os
from work_muxixyz_app import create_app, db
from flask import current_app, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from work_muxixyz_app.models import Team, Group, User, Project, Message, Statu, File, Comment, User2Project
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
        # superuser=User(name='test',email='cat@test.com',tel='11111111111',role=7,team_id=1)
        # muxi.creator=1
        # admin=User(name='test',email='dog@test.com',tel='22222222222',role=1,team_id=1)
        # usr=User(name='test',email='pig@test.com',tel='33333333333',role=1,team_id=1)
        # project=Project(name='test')
        # rela=User2Project(user_id=6,project_id=6)
        # db.session.add(muxi)
        # db.session.add(superuser)
        # db.session.add(admin)
        # db.session.add(usr)
        # db.session.add(project)
        # db.session.add(rela)
        # db.session.commit()
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
            'http://localhost/api/v1.0/project/new/',
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
            'http://localhost/api/v1.0/project/' + pid + '/',
            data=json.dumps({
                "intro": "test1",
                "name": "test1"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    #
    # def test_project_a_3_comments(self):
    #     response = self.client.post(
    #         'http://localhost/api/v1.0/project/1/file/1/comments/',
    #         data = json.dumps({
    #             "content": "test"
    #         }),
    #         headers = self.get_a_api_headers(True)
    #     )
    #     self.assertTrue(response.status_code == 200)
    #
    def test_project_a_4_member(self):
        response = self.client.put(
            'http://localhost/api/v1.0/project/' + pid + '/member/',
            data=json.dumps({
                "userList": [6]
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
    #
    # def test_project_b_1_comment(self):
    #     respons = self.client.get(
    #         'http://localhost/api/v1.0/project/1/file/1/comment/1/',
    #         headers = self.get_a_api_headers(True)
    #     )
    #     self.assertTrue(response.status_code == 200)
    #
    # def test_project_b_2_comments(self):
    #     response = self.client.get(
    #         'http://localhost/api/v1.0/project/1/file/1/comments/',
    #         headers = self.get_a_api_headers(True)
    #     )
    #     self.assertTrue(response.status_code == 200)
    #
    def test_project_b_3_member(self):
        response = self.client.get(
            'http://localhost/api/v1.0/project/' + pid + '/member/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
    #
    def test_project_b_4_project(self):
        response = self.client.get(
            'http://localhost/api/v1.0/project/' + pid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    # def test_project_c_1_comment(self):
    #     response = self.client.delete(
    #         'http://localhost/api/v1.0/project/1/file/1/comment/1/',
    #         headers = self.get_a_api_headers(True)
    #     )
    #     self.assertTrue(response.status_code == 200)
    #
    def test_project_c_2_project(self):
        response = self.client.delete(
            'http://localhost/api/v1.0/project/' + pid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
