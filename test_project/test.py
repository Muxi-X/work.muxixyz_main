import unittest
import os
from work_muxixyz_app import create_app, db
from flask import current_app, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from work_muxixyz_app.models import Team, Group, User, Project, Message, Statu, File, Doc , FolderForFile, FolderForMd, Comment, User2Project
import random
import json
import requests
import time

requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False

class BasicTestCase(unittest.TestCase):

    @classmethod
    def get_a_api_headers(cls, token=False):
        if token:
            return {
                'token': TOKEN,
                'Connection': 'close',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        else:
            return {
                'Accept': 'application/json',
                'Connection': 'close',
                'Content-Type': 'application/json',
            }

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        from work_muxixyz_app.api import api
        self.app.register_blueprint(api, url_prefix='/api/v1.0/')

    def test_z_tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    @classmethod
    def test_a_init(cls):
        team = Team(name='test', count=3, creator=1, time="time")
        group = Group(name="group", count=3, leader=4, time="time")
        db.session.add(group)
        db.session.add(team)
        db.session.commit()
        superuser = User(name='test1', email='cat@test.com', tel='11111111111',
                         role=7, team_id=team.id, group_id=group.id)
        db.session.add(superuser)
        db.session.commit()
        user = User.query.filter_by(id=superuser.id).first()
        global TOKEN
        TOKEN = user.generate_confirmation_token()
        time.sleep(3)

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
        pid = json.loads(response.data.decode('utf-8'))["project_id"]
        self.assertTrue(response.status_code == 201)
        time.sleep(3)

    def test_project_a_2_project(self):
        response = self.client.post(
            url_for('api.ProjectPidPost', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            data=json.dumps({
                "intro": "newtest1",
                "name": "nwetest1"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 201)
        time.sleep(3)

    def test_project_a_3_folder_file(self):
        response = self.client.post(
            url_for('api.FolderFilePost', _external=True),
            data=json.dumps({
                "foldername": "test",
                "project_id": pid,
            }),
            headers=self.get_a_api_headers(True)
        )
        global filefoid
        filefoid = json.loads(response.data.decode('utf-8'))["id"]
        self.assertTrue(response.status_code == 201)
        time.sleep(3)

    def test_project_a_7_folder_doc(self):
        response = self.client.post(
            url_for('api.FolderDocPost', _external=True),
            data=json.dumps({
                "foldername": "test",
                "project_id": pid,
            }),
            headers=self.get_a_api_headers(True)
        )
        global docfoid
        docfoid = json.loads(response.data.decode('utf-8'))["id"]
        self.assertTrue(response.status_code == 201)
        time.sleep(3)

    # # def test_project_a_4_folder(self):
    # #     response = self.client.post(
    # #         url_for('api.ProjectFolder', pid=pid, foid=0, _external=True),
    # #         data=json.dumps({
    # #             "foldername": "test",
    # #             "kind": False
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 201)
    #
    # # def test_project_a_5_file(self):
    # #     response = self.client.post(
    # #         url_for('api.ProjectFile', pid=pid, foid=foid, fid=0, _external=True),
    # #         data = json.dumps({
    # #             "content": "this is the content",
    # #             "filename": "filename1",
    # #             "kind": True
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     global fid
    # #     fid = json.loads(response.data.decode('utf-8'))['fid']
    # #     self.assertTrue(response.status_code == 201)
    #
    #
    # # def test_project_a_6_comments(self):
    # #     response = self.client.post(
    # #         url_for('api.ProjectDcoCommentsPost', pid=pid, fid=fid, _external=True),
    # #         # 'http://localhost/api/v1.0/project/' + pid + '/file/1/comments/',
    # #         data=json.dumps({
    # #             "content": "test"
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     global cid
    # #     cid = json.loads(response.data.decode('utf-8'))['cid']
    # #     self.assertTrue(response.status_code == 201)
    #
    def test_project_a_4_member(self):
        response = self.client.put(
            url_for('api.ProjectMemberPut', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/member/',
            data=json.dumps({
                "userList": [1]
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)

    def test_project_a_5_folder_file(self):
        response = self.client.put(
            url_for('api.FolderFileIdPut', id=filefoid, _external=True),
            data=json.dumps({
                "foldername": "change"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)

    def test_project_a_8_folder_doc(self):
        response = self.client.put(
            url_for('api.FolderDocIdPut', id=docfoid, _external=True),
            data=json.dumps({
                "foldername": "change"
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)

    def test_project_a_6_file_children(self):
        response = self.client.post(
            url_for('api.FolderFileChrildrenPost', _external=True),
            data=json.dumps({
                "folder": [filefoid],
                "file": [],
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)

    def test_project_a_9_doc_children(self):
        response = self.client.post(
            url_for('api.FolderDocChrildrenPost', _external=True),
            data=json.dumps({
                "folder": [docfoid],
                "file": [],
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)

    # def test_project_a_A_file_file_post(self):
    #     files = dict(file=open('/Users/darren/Documents/program/Lesson-C/selectsort.c', 'rb'))
    #     response = requests.post(
    #         url_for('api.FileFilePost', _external=True),
    #         data=json.dumps({
    #             "project_id": pid,
    #         }),
    #         files=files,
    #         headers=self.get_a_api_headers(True)
    #     )
    #     self.assertTrue(response.status_code == 201)
    #     global fileid
    #     fileid = json.loads(response.data.decode('utf-8'))["fid"]
    #     self.assertTrue(response.status_code == 201)
    #
    # def test_project_a_B_file_file_id(self):
    #     response = requests.delete(
    #         url_for('api.FileFileIdDelete', id=fileid, _external=True),
    #         headers=self.get_a_api_headers(True),
    #     )
    #     self.assertTrue(response.status_code == 200)

    def test_project_a_C_file_doc_post(self):
        response = requests.post(
            url_for('api.FileDocPost', _external=True),
            data=json.dumps({
                "project_id": pid,
                "mdname": "request",
                "content": "request",
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 201)
        global docid
        docid = json.loads(response.data.decode('utf-8'))["fid"]
        self.assertTrue(response.status_code == 201)
        time.sleep(3)

    def test_project_a_E_file_doc_id(self):
        response = requests.delete(
            url_for('api.FileDocIdDelete', id=docid, _external=True),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)

    def test_project_a_D_file_doc_put(self):
        response = requests.post(
            url_for('api.FileDocIdPut', id=docid, _external=True),
            data=json.dumps({
                "DocName": "request.get_json().get('mdname')",
                "content": "request.get_json().get('content')",
            }),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 201)
        time.sleep(3)

    # # def test_project_a_9_file(self):
    # #     response = self.client.put(
    # #         url_for('api.ProjectFile', pid=pid, foid=foid, fid=fid, _external=True),
    # #         data = json.dumps({
    # #             "filename": "changefiadamej",
    # #             "content": "changecontentgf"
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_a_a_file(self):
    # #     response = self.client.put(
    # #         url_for('api.ProjectF', pid=pid, foid=foid, toid=1, _external=True),
    # #         data = json.dumps({
    # #             "kind": 1
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_a_b_file(self):
    # #     response = self.client.put(
    # #         url_for('api.ProjectF', pid=pid, foid=fid, toid=foid, _external=True),
    # #         data = json.dumps({
    # #             "kind": 2
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_b_1_comment(self):
    # #     response = self.client.get(
    # #         url_for('api.ProjectFileCommentGet', pid=pid, fid=fid, cid=cid, _external=True),
    # #         # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comment/' + cid + '/',
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_b_2_comments(self):
    # #     response = self.client.get(
    # #         url_for('api.ProjectFileComments', pid=pid, fid=fid, _external=True),
    # #         # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comments/',
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    def test_project_b_2_member(self):
        response = self.client.get(
            url_for('api.ProjectMemberGet', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/member/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)

    def test_project_b_1_project(self):
        response = self.client.get(
            url_for('api.ProjectPidGet', pid=pid, _external=True),
            # 'http://localhost/api/v1.0/project/' + pid + '/',
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)

    def test_project_b_3_file_doc_id_get(self):
        response = requests.get(
            url_for('api.FileDocIdGet', id=docid, _external=True),
            headers=self.get_a_api_headers(True)
        )
        self.assertTrue(response.status_code == 200)
        time.sleep(3)
    #
    # def test_project_b_4_project(self):
    #     response = self.client.get(
    #         url_for('api.FolderFileIdPut', foid=filefoid, _external=True),
    #         headers=self.get_a_api_headers(True)
    #     )
    #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_b_6_project(self):
    # #     response = self.client.get(
    # #         url_for('api.ProjectFile', pid=pid, foid=foid, fid=fid, _external=True),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_b_7_file(self):
    # #     response = self.client.post(
    # #         url_for('api.ProjectRe', pid=pid, _external=True),
    # #         data = json.dumps({
    # #             "id": foid,
    # #             "kind": 2
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_b_8_file(self):
    # #     response = self.client.get(
    # #         url_for('api.ProjectRe', pid=pid, _external=True),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_b_9_file(self):
    # #     response = self.client.put(
    # #         url_for('api.ProjectRe', pid=pid, _external=True),
    # #         data = json.dumps({
    # #             "id": foid,
    # #             "kind": 2
    # #         }),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_c_1_comment(self):
    # #     response = self.client.delete(
    # #         url_for('api.ProjectFileCommentDelete', pid=pid, fid=fid, cid=cid, _external=True),
    # #         # 'http://localhost/api/v1.0/project/' + pid + '/file/' + fid + '/comment/' + cid + '/',
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # def test_project_c_5_project(self):
    #     response = self.client.delete(
    #         url_for('api.ProjectPidDelete', pid=pid, _external=True),
    #         # 'http://localhost/api/v1.0/project/' + pid + '/',
    #         headers=self.get_a_api_headers(True)
    #     )
    #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_c_4_file(self):
    # #     response = self.client.delete(
    # #         url_for('api.ProjectFolder', pid=pid, foid=str(int(foid)+1), _external=True),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
    #
    # # def test_project_c_3_file(self):
    # #     response = self.client.delete(
    # #         url_for('api.ProjectFile', pid=pid, foid=foid, fid=fid, _external=True),
    # #         headers=self.get_a_api_headers(True)
    # #     )
    # #     self.assertTrue(response.status_code == 200)
