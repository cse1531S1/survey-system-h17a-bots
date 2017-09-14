#!/usr/bin/env python3
# encoding: utf-8

from flask_httpauth import HTTPBasicAuth
from ..models import User
from flask import g, jsonify, request
from .errors import unauthorized, forbidden
from . import api
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(name_or_token, password):
    if name_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(name_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=name_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.route('/logoff', methods=['GET', 'POST'])
def log_off():
    g.current_user = None
    return jsonify({
        'success': True
    })


@api.route('/get_info')
def get_info():
    # print(request.headers['X-Token'])
    try:
        token = request.args['token']
    except:
        return unauthorized('Invalid credentials')

    user = User.verify_auth_token(token)
    if not user:
        print('blah')
        return unauthorized('Invalid credentials')
    return jsonify({
        'role': ['admin'],
        'name': 'admin',
        'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
        'token': user.generate_auth_token(),
        'introduction': 'super admin'
    })
    pass


@api.route('/get_token', methods=['POST', 'GET'])
def get_token():
    # print(request.headers)
    data = request.get_json()
    user = User.get_by_name(data['username'])
    if verify_password(data['username'], data['password']):
        g.current_user = user
        return jsonify({
            'success': True,
            'token': user.generate_auth_token()
        })
    return jsonify({
        'error': 'Invalid credentials!'
    })
