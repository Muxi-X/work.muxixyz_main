import unittest
import os
from work_muxixyz_app import create_app,db
from flask import current_app,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from work_muxixyz_app.models import Team,Group,User,Project,User2Project,Message,Statu,File,Comment
import random
import json

# db=SQLAlchemy()

class BasicTestCase(unittest.TestCase):

    def get_api_headers(self,ifToken):
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

# API FOR GET A TOKEN AND PREPARTION

    def test_management_a_auth(self):
        muxi=Team(name='test',count=3)
        superuser=User(name='cat',email='cat@test.com',tel='11111111111',role=7,team_id=1)
        muxi.creator=1
        admin=User(name='dog',email='dog@test.com',tel='22222222222',role=1,team_id=1)
        usr=User(name='pig',email='pig@test.com',tel='33333333333',role=1,team_id=1)
        project=Project(name='test')
        rela=User2Project(user_id=1,project_id=1)
        db.session.add(muxi)
        db.session.add(superuser)
        db.session.add(admin)
        db.session.add(usr)
        db.session.add(project)
        db.session.add(rela)
        db.session.commit()
        response=self.client.post(
            url_for('api.login',_external=True),
            data=json.dumps({
                "username": 'cat',
            }),
            headers=self.get_api_headers(False),
        )
        s=json.loads(response.data.decode('utf-8'))['token']
        global TOKEN
        TOKEN=s
        print ('OK')
# END

# API FOR MANAGEMENT START

    def test_management_a_newgroup(self):
        response=self.client.post(
            url_for('api.NewGroup',_external=True),
            data=json.dumps({
                "groupName": 'test',
                "userlist": list([3]),
            }),
            headers=self.get_api_headers(True)
        )
#        print (response.status_code)
        self.assertTrue(response.status_code==200)

    def test_management_b_groupuserlist(self):
        response=self.client.get(
            'http://localhost/api/v1.0/group/1/userList',
            headers=self.get_api_headers(True)
        )
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['list']
#        print (s)

    def test_management_c_grouplist(self):
        response=self.client.get(
            url_for('api.GroupList',_external=True),
            headers=self.get_api_headers(True)
        )
 #       print(response.status_code)
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['groupList']
#        print (s)

    def test_management_d_projectuserlist(self):
        response=self.client.get(
            'http://localhost/api/v1.0/project/1/userList/',
#            url_for(api.ProjectUserList,_external=True),
            headers=self.get_api_headers(True)
        )
#        print(response.status_code)
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['list']
#        print (s)

    def test_management_e_userprojectlist(self):
        response=self.client.get(
            'http://localhost/api/v1.0/user/project/list/',
            headers=self.get_api_headers(True)
        )
#        print(response.status_code)
        self.assertTrue(response.status_code==200)
        s=json.loads(response.data.decode('utf-8'))['projectList']
#       print (s)

    def test_management_f_2bmember(self):
        newone=User(name='freshman',role=0)
        db.session.add(newone)
        db.session.commit()
        response=self.client.post(
            url_for('api.User2bMember',_external=True),
            data=json.dumps({
                "userID": newone.id,
	            }),
            headers=self.get_api_headers(True)
        )
#        print (response.status_code)
        self.assertTrue(response.status_code==200)

    def test_management_g_addadmin(self):
        response=self.client.post(
            url_for('api.AddAdmin',_external=True),
            data=json.dumps({
                "luckydog": 'freshman',
            }),
            headers=self.get_api_headers(True)
        )
#        print(response.status_code)
        self.assertTrue(response.status_code==200)

    def test_management_h_usermanageproject(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/2/managePro/',
            data=json.dumps({
                "projectList": list([1]),
            }),
            headers=self.get_api_headers(True)
        )
        self.assertTrue(response.status_code==200)

    def test_management_i_usermanagegroup(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/2/manageGroup/',
            data=json.dumps({
                "groupID": 1,
            }),
            headers=self.get_api_headers(True)
        )
        self.assertTrue(response.status_code==200)

    def test_management_j_setrole(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/2/setRole/',
            data=json.dumps({
                "role": 2,
            }),
            headers=self.get_api_headers(True)
        )
        self.assertTrue(response.status_code==200)

    def test_management_k_usersetting(self):
        response=self.client.post(
            'http://localhost/api/v1.0/user/1/setting/',
            data=json.dumps({
                "username": 'test',
                'address': 'test',
                'tel': '11111111111',
                'message': True,
                'email': False,
            }),
            headers=self.get_api_headers(True)
        )
        self.assertTrue(response.status_code==200)

# API FOR MANAGEMENT END
