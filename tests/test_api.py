import unittest
import json
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role


class APITestCase(unittest.TestCase):
    def setUp(self):
        print('')
        print('Setting up database with user roles...')
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        print('Database successfully set up with user roles.')

    def tearDown(self):
        print('')
        print('Destroying database...')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print('Database successfully destroyed.')

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
        print('')
        print('Trying to access a page that does not exist...')
        response = self.client.get(
            '/not/exists/page',
            headers=self.get_api_headers('username', 'password'))
        self.assertTrue(response.status_code == 404)
        print('Appropriate status code was given in response.')

    def test_no_auth(self):
        print('')
        print('Trying to fetch courses without authentication...')
        response = self.client.get(
            url_for('api.fetch_course'), content_type='application/json')
        self.assertTrue(response.status_code == 200)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to get pie chart data without authentication...')
        response = self.client.get(
            url_for('api.fetch_pie_chart'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch answers without authentication...')
        response = self.client.get(
            url_for('api.fetch_answer'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch all surveys without authentication...')
        response = self.client.get(
            url_for('api.fetch_all_survey'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to modify a survey without authentication...')
        response = self.client.get(
            url_for('api.modify_survey'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to verify an unverified guest user without authentication...')
        response = self.client.get(
            url_for('api.verify_user'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch a question without authentication...')
        response = self.client.get(
            url_for('api.fetch_question'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch questions for the question pool without authentication...')
        response = self.client.get(
            url_for('api.question_pool'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to create a survey without authentication...')
        response = self.client.get(
            url_for('api.create_survey'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to create a question without authentication...')
        response = self.client.get(
            url_for('api.create_question'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to delete a question without authentication...')
        response = self.client.get(
            url_for('api.delete_question'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch student response statistics data without authentication...')
        response = self.client.get(
            url_for('api.srstatic'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to register without authentication...')
        response = self.client.get(
            url_for('api.register'), content_type='application/json')
        self.assertTrue(response.status_code == 200)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch guest pool data without authentication...')
        response = self.client.get(
            url_for('api.guest_pool'), content_type='application/json')
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))

    def test_bad_auth(self):
        # add a user
        print('')
        print('Creating an administrator user...')
        r = Role.query.filter_by(name='admin').first()
        self.assertIsNotNone(r)
        u = User(username='admin', password='cat', role=r)
        db.session.add(u)
        db.session.commit()
        print('Successfully created an administrator user.')

        # authenticate with bad password
        print('Trying to fetch guest pool with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.guest_pool'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch a course with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.fetch_course'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 200)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to get data for pie chart generation with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.fetch_pie_chart'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch answers for a question with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.fetch_answer'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch all surveys with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.fetch_all_survey'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to modify a survey with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.modify_survey'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to verify a guest user with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.verify_user'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch questions for a survey with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.fetch_question'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch question pool data with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.question_pool'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to create a survey with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.create_survey'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to create a question with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.create_question'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to delete a question with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.delete_question'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch the survey response statistics with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.srstatic'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to register for a guest account with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.register'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 200)
        print('Appropriate response was returned. Code: ' + str(response.status_code))
        print('Trying to fetch the guest pool data with the wrong authentication credentials...')
        response = self.client.get(
            url_for('api.guest_pool'), headers=self.get_api_headers('admin', 'dog'))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))

    def test_token_auth(self):
        print('')
        # add a user
        print('Creating an administrator user...')
        r = Role.query.filter_by(name='admin').first()
        self.assertIsNotNone(r)
        u = User(username='admin', password='cat', role=r)
        db.session.add(u)
        db.session.commit()
        print('Successfully created an administrator user.')

        # issue a request with a bad token
        print('Trying to send a request with a bad token...')
        response = self.client.get(
            url_for('api.guest_pool'),
            headers=self.get_api_headers('bad-token', ''))
        self.assertTrue(response.status_code == 401)
        print('Appropriate response was returned. Code: ' + str(response.status_code))

        # get a token
        print('Trying to request for a token...')
        response = self.client.get(
            url_for('api.get_token'), headers=self.get_api_headers('admin', 'cat'),
            data=json.dumps({'username': 'admin', 'password': 'cat'}))
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        print('Valid token returned within response.')
        token = json_response['token']
        print('Token successfully requested.')

        # issue a request with the token
        print('Trying to send a request with a valid token...')
        response = self.client.get(
            url_for('api.guest_pool'),
            headers=self.get_api_headers(token, ''))
        self.assertTrue(response.status_code == 200)
        print('Appropriate response was returned. Code: ' + str(response.status_code))

    def test_unverified(self):
        # add an unverified user
        print('')
        print('Creating an unverified guest user...')
        r = Role.query.filter_by(name='guest').first()
        self.assertIsNotNone(r)
        u = User(username='guest', password='cat', verified=False, role=r)
        db.session.add(u)
        db.session.commit()
        print('Unverified guest user successfully created.')

        # get list of posts with the unverified account
        print('Trying to log in as an unverified guest...')

        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('guest', 'cat'),
            data=self.get_api_data('guest', 'cat')
        )
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response.get('unverified'))
        print('Appropriate response was returned. User was determined as unverified.')
        print('')
