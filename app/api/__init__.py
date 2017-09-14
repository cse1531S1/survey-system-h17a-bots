#!/usr/bin/env python3
# encoding: utf-8

from flask import Blueprint

api = Blueprint('api', __name__)

from . import survey_handler, authentication
