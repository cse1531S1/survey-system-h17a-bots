#!/usr/bin/env python3
# encoding: utf-8

from flask_httpauth import HTTPBasicAuth
from ..models import User, Course
from flask import g, jsonify, request
from .errors import unauthorized
from . import api
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(name_or_token, password):
    """
    This function is used to verify users' password.
    """

    if name_or_token == '':
        g.current_user = None
        return False
    if password == '':
        g.current_user = User.verify_auth_token(name_or_token)
        g.token_used = True
        return g.current_user is not None

    # try:
        # token = request.headers['X-Token']
        # g.current_user = User.verify_auth_token(token)
        # return g.current_user is not None
    # except:
        # pass

    user = User.query.filter_by(username=name_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """
    Authentication error handler
    """

    return unauthorized('Invalid credentials')


@api.route('/logoff', methods=['GET', 'POST'])
def log_off():
    """
    Log off the system
    """

    g.current_user = None
    return jsonify({
        'success': True
    })


@api.route('/get_info')
@auth.login_required
def get_info():
    """
    Get User infomation (Login required).
    """

    user = g.current_user
    courses = Course.get_all()
    loaded = False
    if len(courses) != 0:
        loaded = True

    if not user:
        return unauthorized('Invalid credentials')
    rtn = jsonify({
        'role': [user.role.name],
        'name': user.username,
        'avatar': '',
        'courses': [i.course_code for i in user.courses.all()],
        'token': user.generate_auth_token(),
        'success': True,
        'loaded': loaded,
        'introduction': ''
    })

    return rtn


# @auth.login_required
@api.route('/get_token', methods=['POST', 'GET'])
def get_token():
    """
    Generate token for current user,
    who is not anonymous and has been verified
    """

    try:
        if g.current_user.is_anonymous:
            return unauthorized('Invalid credentials')
    except:
        data = request.get_json()
        if not verify_password(data['username'], data['password']):
            return jsonify({
                'success': False
            })

    if g.current_user.verified is False:
        return jsonify({
            'unverified': True
        })

    return jsonify({
        'token': g.current_user.generate_auth_token(
            expiration=360000),
        'expiration': 360000,
        'success': True
    })
