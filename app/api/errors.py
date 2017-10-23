#!/usr/bin/env python3
# encoding: utf-8

from flask import jsonify
from . import api


class ValidationError(ValueError):
    pass


def bad_request(message):
    """
    error 400, bad request
    """

    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    """
    error 401, unauthorized
    """

    response = jsonify({'error': 'unauthorized', 'message': message, 'code': 50008})
    response.status_code = 401
    return response


def forbidden(message):
    """
    error 403, forbidden
    """

    response = jsonify({'error': 'forbidden', 'message': message, 'code': 50008})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
