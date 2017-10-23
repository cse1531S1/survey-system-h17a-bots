#!/usr/bin/env python3
# encoding: utf-8

import unittest
from flask import current_app
from app import create_app, db


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        print('')
        print('Setting up database...')
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        print('Database successfully set up.')

    def tearDown(self):
        print('')
        print('Destroying database...')
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print('Database successfully destroyed.')

    def test_app_exists(self):
        print('')
        print('Testing if the application exists...')
        self.assertFalse(current_app is None)
        print('Application exists. Illuminati confirmed.')

    def test_app_is_testing(self):
        print('')
        print('Testing if the application is testing the tests...')
        self.assertTrue(current_app.config['TESTING'])
        print('Test successful. The application is testing its test testing the tests.')
