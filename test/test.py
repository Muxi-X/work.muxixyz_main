import unittest
import os
from work_muxixyz_app import create_app,db
from flask import current_app,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import json

# db=SQLAlchemy()

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(os.getenv('FLASK_CONFIG') or 'default')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

#    def tearDown(self):
#        db.session.remove()
#        db.drop_all()
#        db.create_all()
#        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

# API FOR MANAGEMENT START

    def test_management_a_newgroup(self):
        response=self.client.post(
            url_for('api.GroupUserlist',_external=True),
            data=json.dumps({
                "groupName": 'test',
                "userlist": {3} 
            }),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)

    def test_management_b_groupuserlist(self):
        response=self.client.get(
            'http://localhost/api/v1.0/group/1/userList',            
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['list']
        print (s)

    def test_management_c_grouplist(self):
        response=self.client.get(
            url_for('api.GroupList',_external=True),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['list']
        print (s)

    def test_management_d_projectuserlist(self):
        response=self.client.get(
            'http://localhost/api/v1.0/project/1/userList',            
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['list']
        print (s)

    def test_management_e_userprojectlist(self):
        response=self.client.get(
            'http://localhost/api/v1.0/user/1/project/list',
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['list']
        print (s)

    def test_management_f_2bmember(self):
        response=self.client.post(
            url_for('api.2bMember',_external=True),
            data=json.dumps({
                "userID": 1,
            }),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)

    def test_management_g_addadmin(self):
        response=self.client.post(
            url_for('api.AddAdmin',_external=True),
            data=json.dumps({
                "luckdog": 'luckdog',
            }),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)

    def test_management_h_usermanageproject(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/2/managePro',
            data=json.dumps({
                "projectList": {1},
            }),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)

    def test_management_i_usermanagegroup(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/2/manageGroup',
            data=json.dumps({
                "groupID": 1,
            }),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)

    def test_management_j_setrole(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/2/setRole',
            data=json.dumps({
                "role": 2,
            }),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)

    def test_management_k_usersetting(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/1/setting',
            data=json.dumps({
                "username": 'test',
                'address': 'test',
                'tel': '11111111111',
                'message': True,
                'email': False,
            }),
            content_type='application/json'
        )
        self.assertTrue(response.status_code==200)

# API FOR MANAGEMENT END
