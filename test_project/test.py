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
        muxi=Team(name='test', count=3, creator=1)
        db.session.add(muxi)
        db.session.commit()
        superuser=User(name='test1',email='cat@test.com',tel='11111111111',role=7,team_id=muxi.id)
        admin=User(name='test2',email='dog@test.com',tel='22222222222',role=1,team_id=muxi.id)
        usr=User(name='test3',email='pig@test.com',tel='33333333333',role=1,team_id=muxi.id)
        db.session.add(superuser)
        db.session.add(admin)
        db.session.add(usr)
        db.session.commit()
        # project=Project(name='test')
        # db.session.add(project)
        # db.session.commit()
        # rela=User2Project(user_id=superuser.id,project_id=project.id)
        # folder = Folder(name='test', project_id=project.id, kind=True)
        # db.session.add(folder)
        # db.session.commit()
        # file = File(filename='test', kind=True, editor_id=superuser.id, creator_id=superuser.id, folder_id=folder.id, project_id=project.id, url='http://pdw7hnao1.bkt.clouddn.com/changefilename%2009-57-20-432.md')
        # statu = Statu(content='test', time='test', like=1, comment=1, user_id=superuser.id, )
        # db.session.add(rela)
        # db.session.add(file)
        # db.session.add(statu)
        # db.session.commit()
        # pid = str(project.id)
        # foid = str(folder.id)
        # fid = str(file.id)
        response = self.client.post(
            url_for('api.login', _external=True),
            data=json.dumps({
                "username": 'test1',
            }),
            headers=self.get_a_api_headers(False),
        )
        s = json.loads(response.data.decode('utf-8'))['token']
        global TOKEN
        TOKEN = s

    def test_project_a_1_new(self):
        response = self.client.post(
            url_for('api.ProjectNew', _external=True),
            # 'http://localhost/api/v1.0/project/new/',
            data=json.dumps({
                "username": "test1",
                "projectname": "test1",
                "userlist": [
                    {
                        "userID": 1,
                       "userName": "test"
                    }
                ],
                "intro": "test"
            }),
            headers=self.get_a_api_headers(True)
        )
        global pid
        pid = json.loads(response.data.decode('utf-8'))['project_id']
        self.assertTrue(response.status_code == 201)

    def test_project_a_2_project(self):
        response = self.client.post(
            url_for('api.ProjectPidPost', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            data=json.dumps({
                "intro": "test1",
                "name": "test1"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 201)

    def test_project_a_3_folder(self):
        response = self.client.post(
            url_for('api.ProjectFolder', pid=pid, foid=0, _external=True),
            data=json.dumps({
                "foldername": "test",
                "kind": True
            }), 
            headers=self.get_a_api_headers(True)
        )
        global foid
        foid = json.loads(response.data.decode('utf-8'))['foid']
        self.assertTrue(response.status_code == 201)

    def test_project_a_4_folder(self):
        response = self.client.post(
            url_for('api.ProjectFolder', pid=pid, foid=0, _external=True),
            data=json.dumps({
                "foldername": "test",
                "kind": False
            }), 
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 201)

    def test_project_a_5_file(self):
        response = self.client.post(
            url_for('api.ProjectFile', pid=pid, foid=foid, fid=0, _external=True),
            data = json.dumps({
                "content": "this is the content",
                "filename": "filename1",
                "kind": True
            }),
            headers=self.get_a_api_headers(True)
        )
        global fid
        fid = json.loads(response.data.decode('utf-8'))['fid']
        self.assertTrue(response.status_code == 201)


    def test_project_a_6_comments(self):
        response = self.client.post(
            url_for('api.ProjectFileCommentsPost', pid=pid, fid=fid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/1/comments/',
            data=json.dumps({
                "content": "test"
            }),
            headers=self.get_a_api_headers(True)
        )
        global cid
        cid = json.loads(response.data.decode('utf-8'))['cid']
        self.assertTrue(response.status_code == 201)

    def test_project_a_7_member(self):
        response = self.client.put(
            url_for('api.ProjectMemberPut', pid=pid, fid=fid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/member/',
            data=json.dumps({
                "userList": [1, 6]
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_a_8_file(self):
        response = self.client.put(
            url_for('api.ProjectFolder', pid=pid, foid=foid, _external=True),
            data = json.dumps({
                "foldername": "change"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_a_9_file(self):
        response = self.client.put(
            url_for('api.ProjectFile', pid=pid, foid=foid, fid=fid, _external=True),
            data = json.dumps({
                "filename": "changefiadamej",
                "content": "changecontentgf"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_a_a_file(self):
        response = self.client.put(
            url_for('api.ProjectF', pid=pid, foid=foid, toid=1, _external=True),
            data = json.dumps({
                "kind": 1
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_a_b_file(self):
        response = self.client.put(
            url_for('api.ProjectF', pid=pid, foid=fid, toid=foid, _external=True),
            data = json.dumps({
                "kind": 2
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_1_comment(self):
        response = self.client.get(
            url_for('api.ProjectFileCommentGet', pid=pid, fid=fid, cid=cid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comment/' + cid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_2_comments(self):
        response = self.client.get(
            url_for('api.ProjectFileComments', pid=pid, fid=fid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comments/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_3_member(self):
        response = self.client.get(
            url_for('api.ProjectMemberGet', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/member/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_4_project(self):
        response = self.client.get(
            url_for('api.ProjectPidGet', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            headers=self.get_a_api_headers(True)
        )   
        self.assertTrue(response.status_code == 200)

    def test_project_b_5_project(self):
        response = self.client.get(
            url_for('api.ProjectFolder', pid=pid, foid=foid, _external=True),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_6_project(self):
        response = self.client.get(
            url_for('api.ProjectFile', pid=pid, foid=foid, fid=fid, _external=True),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_b_7_file(self):
        response = self.client.post(
            url_for('api.ProjectRe', pid=pid, _external=True),
            data = json.dumps({
                "id": foid,
                "kind": 2
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
    
    def test_project_b_8_file(self):
        response = self.client.get(
            url_for('api.ProjectRe', pid=pid, _external=True),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
    
    def test_project_b_9_file(self):
        response = self.client.put(
            url_for('api.ProjectRe', pid=pid, _external=True),
            data = json.dumps({
                "id": foid,
                "kind": 2
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_c_1_comment(self):
        response = self.client.delete(
            url_for('api.ProjectFileCommentDelete', pid=pid, fid=fid, cid=cid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comment/' + cid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_c_2_project(self):
        response = self.client.delete(
            url_for('api.ProjectPidDelete', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_c_4_file(self):
        response = self.client.delete(
            url_for('api.ProjectFolder', pid=pid, foid=str(int(foid)+1), _external=True),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_c_3_file(self):
        response = self.client.delete(
            url_for('api.ProjectFile', pid=pid, foid=foid, fid=fid, _external=True),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
