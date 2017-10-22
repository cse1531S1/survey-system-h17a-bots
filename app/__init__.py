#!/usr/bin/env python3
# encoding: utf-8

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
import os


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()


APP_DIR = os.path.dirname(__file__)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    CORS(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    from .api import api as api_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint, url_prefix='/api/v1.0')

    return app
