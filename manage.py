#!/usr/bin/env python3
# encoding: utf-8

import os
from app import create_app, db
from app.models import User, Survey, Answer, Question, Answer, Choice, Course, AnswerEntity
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Survey=Survey, Answer=Answer, Course=Course,
                Question=Question, AnswerEntity=AnswerEntity, Choice=Choice)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
