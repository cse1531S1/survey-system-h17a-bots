#!/usr/bin/env python3
# encoding: utf-8

from app import create_app, db
from app.models import User, Survey, Answer, Question, Choice, Course, AnswerEntity, Role
from flask_script import Manager, Shell
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Survey=Survey, Answer=Answer, Course=Course,
                Question=Question, AnswerEntity=AnswerEntity, Choice=Choice, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def reset():
    """Reset database and insert admin."""
    db.drop_all()
    db.create_all()
    Role.insert_roles()
    a = User(username='admin', password='123', role=Role.get_by_name('admin'))
    db.session.add(a)
    db.session.commit()


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == '__main__':
    manager.run()
