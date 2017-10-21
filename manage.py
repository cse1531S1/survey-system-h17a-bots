#!/usr/bin/env python3
# encoding: utf-8

import os
from app import create_app, db
from app.models import User, Survey, Answer, Question, Choice, Course, AnswerEntity, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Survey=Survey, Answer=Answer, Course=Course,
                Question=Question, AnswerEntity=AnswerEntity, Choice=Choice, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def reset():
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    a = User(username='admin', password='123', role=Role.get_by_name('admin'))
    db.session.add(a)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
