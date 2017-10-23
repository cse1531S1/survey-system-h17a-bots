import unittest
from flask import url_for
from app import create_app, db
from app.models import Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        print('')
        print('Setting up database...')
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)
        print('Database successfully set up.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def tearDown(self):
        print('')
        print('Destroying database...')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print('Database successfully destroyed.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')

    def test_home_page(self):
        print('')
        print('Trying to access the index page...')
        response = self.client.get(url_for('main.index'))
        self.assertTrue(b'Survey Manage' in response.data)
        print('Index page successfully returned.')
        print('\x1b[0;32;40m' + 'pass' + '\x1b[0m')
        print('')
