'''coding = utf-8'''
import unittest
import os
import random
import json
from flask import current_app, url_for#, jsonify, Flask
from work_muxixyz_app import create_app, db
from work_muxixyz_app.models import Feed, Team, User, Group, Project, Message, Statu, File, Comment, User2Project

#db = SQLAlchemy()
FROM = ['status', 'project', 'doc','team', 'comments', 'teams', 'user', 'file']
KIND = random.randint(0, 6)
SOURCEID = 1#random.randint(1, 100)

class SampleTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            os.getenv('FLASK_CONFIG') or 'default')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()




    def get_api_headers(self, iftoken):
        if iftoken is True:
            return {
                'token': TOKEN,
                'Accept': 'application/json',
                'Content-Type': 'application/json'}
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'}

 
    def test_1_app_exist(self):
        self.assertFalse(current_app is None)


    def test_a_management_auth(self):
        muxi = Team(name='Teamtest', count=3, creator=1)
        db.session.add(muxi)
        db.session.commit()
        superuser = User(
            name='cat',
            email='cat@test.com',
            tel='11111111111',
            role=7,
            team_id=1)
        db.session.add(superuser)
        db.session.commit()
        admin = User(
            name='dog',
            email='dog@test.com',
            tel='22222222222',
            role=1,
            team_id=1)
        db.session.add(admin)
        db.session.commit()
        usr = User(
            name='pig',
            email='pig@test.com',
            tel='33333333333',
            role=1,
            team_id=1)
        db.session.add(usr)
        db.session.commit()
        project = Project(name='test')
        db.session.add(project)
        db.session.commit()
        rela = User2Project(user_id=1, project_id=1)
        db.session.add(rela)
        db.session.commit()
        file1 = File(url='test',project_id=1)
        db.session.add(file1)
        db.session.commit()
        response = self.client.post(
            url_for('api.login', _external=True),
            data=json.dumps({
                "username": 'cat'}),
            headers=self.get_api_headers(False))
        result_t = json.loads(response.data.decode('utf-8'))['token']
        global TOKEN
        TOKEN = result_t


# status PART
    
#    def test_b_1_sharedoc(self):
#       response = self.client.get(
#            url_for('api.sharedoc', docid=1, _external=True),
#            headers=self.get_api_headers(True))
#        global url
#        url = response.data
#        self.assertTrue(response.status_code == 200)
    
    
#    def test_b_2_sharedoc(self):
#        response = self.client.get(
#            url_for('api.viewdoc', url=url, _external=True),
#            headers=self.get_api_headers(True))
#        print(response.data)
#        self.assertTrue(response.status_code == 200)

    
    def test_b_status_new(self):
        response = self.client.post(
            url_for('api.newstatus', _external=True),
            data=json.dumps({
                "content": 'test',
                "title": 'August 24'}),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
    

    def test_c_1_status_like(self):
        response = self.client.put(
            url_for('api.like', sid = 1, _external=True),
            data=json.dumps({
                "iflike": 1}),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)

    def test_c_2_status_get(self):
        response = self.client.get(
            url_for('api.getstatu', sid = 1, _external=True),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
        #print(response.data)

    def test_c_3_status_edit(self):
        response = self.client.put(
            url_for('api.editstatu', sid = 1, _external=True),
            data=json.dumps({
                "content": 'excited',
                "title": 'August 29'}),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
            

    def test_d_status_list(self):
        response = self.client.get(
            url_for('api.statulist', page = 1, _external=True),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
        #print(response.data)
    
    
    def test_e_user_status_list(self):
        response = self.client.get(
            url_for('api.user_statulist', userid = 1, page = 1, _external=True),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
        #print(response.data)
    
    
    def test_f_comment_new(self):
        response = self.client.post(
            url_for('api.newcomments', sid=1, _external=True),
            data=json.dumps({
                "content": 'testcomment'}),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
    
    '''    
    def test_g_comment_get(self):
        response = self.client.get(
            url_for('api.getcomment', sid = 1, cid = 1, _external=True),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
        #print(response.data)
    '''
    '''
    def test_h_comment_getlist(self):
        response = self.client.get(
            url_for('api.getcommentlist', sid = 1, _external=True),
            headers=self.get_api_headers(True))
        self.assertTrue(response.status_code == 200)
        #print(response.data)
    '''
    
    def test_i_comment_delete(self):
        response = self.client.delete(
            url_for('api.deletecomment', sid = 1, cid = 1, _external=True),
            headers=self.get_api_headers(True))
        #print(response.data)
        self.assertTrue(response.status_code == 200)
    
    
    def test_j_status_delete(self):
        response = self.client.delete(
            url_for('api.deletestatu', sid = 1, _external=True),
            headers=self.get_api_headers(True))
        #print(response.data)
        self.assertTrue(response.status_code == 200)
