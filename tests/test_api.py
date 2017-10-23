import unittest
import json
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_api_data(self, username, password):
        return json.dumps({'username': username, 'password': password})

    def test_404(self):
        response = self.client.get(
            '/not/exists/page',
            headers=self.get_api_headers('username', 'password'))
        self.assertTrue(response.status_code == 404)

    def test_no_auth(self):
        response = self.client.get(
            url_for('api.fetch_course'), content_type='application/json')
        self.assertTrue(response.status_code == 200)
        response = self.client.get(
            url_for('api.fetch_pie_chart'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.fetch_answer'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.fetch_all_survey'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.modify_survey'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.verify_user'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.fetch_question'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.question_pool'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.create_survey'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.create_question'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.delete_question'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.srstatic'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.register'), content_type='application/json')
        self.assertTrue(response.status_code == 200)
        response = self.client.get(
            url_for('api.guest_pool'), content_type='application/json')
        self.assertTrue(response.status_code == 401)

    def test_bad_auth(self):
        # add a user
        r = Role.query.filter_by(name='admin').first()
        self.assertIsNotNone(r)
        u = User(username='admin', password='cat', role=r)
        db.session.add(u)
        db.session.commit()

        # authenticate with bad password
        response = self.client.get(
            url_for('api.guest_pool'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.fetch_course'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 200)
        response = self.client.get(
            url_for('api.fetch_pie_chart'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.fetch_answer'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.fetch_all_survey'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.modify_survey'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.verify_user'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.fetch_question'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.question_pool'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.create_survey'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.create_question'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.delete_question'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.srstatic'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        response = self.client.get(
            url_for('api.register'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 200)
        response = self.client.get(
            url_for('api.guest_pool'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)

    def test_token_auth(self):
        # add a user
        r = Role.query.filter_by(name='admin').first()
        self.assertIsNotNone(r)
        u = User(username='admin', password='cat', role=r)
        db.session.add(u)
        db.session.commit()

        # issue a request with a bad token
        response = self.client.get(
            url_for('api.guest_pool'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)

        # get a token
        response = self.client.get(
            url_for('api.get_token'), headers=self.get_api_headers('admin', 'cat'),
            data=json.dumps({'username': 'admin', 'password': 'cat'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']

        # issue a request with the token
        response = self.client.get(
            url_for('api.guest_pool'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)

    def test_unverified(self):
        # add an unverified user
        r = Role.query.filter_by(name='guest').first()
        self.assertIsNotNone(r)
        u = User(username='guest', password='cat', verified=False, role=r)
        db.session.add(u)
        db.session.commit()

        # get list of posts with the unverified account
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('guest', 'cat'),
            data=self.get_api_data('guest', 'cat')
        )
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response.get('unverified'))
