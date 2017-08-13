#!/usr/bin/env python3
# encoding: utf-8

from flask import request, redirect, render_template, abort, g
from . import main


@main.route('/', methods=['GET'])
def index():
    return 'hello world'
