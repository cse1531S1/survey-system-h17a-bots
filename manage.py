#!/usr/bin/env python3
# encoding: utf-8

from app import create_app, db
from app.models import User, Survey, Answer, Question, Choice, Course, AnswerEntity, Role
from flask_script import Manager, Shell
import os
import csv
import re

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
    """
    Reset database and insert admin.
    """

    db.drop_all()
    db.create_all()
    Role.insert_roles()
    a = User(username='admin', password='123', role=Role.get_by_name('admin'))
    db.session.add(a)
    db.session.commit()


@manager.command
def run():
    """
    Run the survey system
    """

    app.run(port=9528)


@manager.command
def load():
    """
    load all courses and students into the database
    """

    print('Loading data from the CSV files. Please note that this might take about 5 minutes')
    with open('courses.csv', 'r') as file_in:
        result = map(str, csv.reader(file_in))
        # match '["ZZZZ9999 99z9"]' like string and get the
        # alphanumeric
        pattern = r'..([A-Z]{4}[0-9]{4})..\s.([0-9]{2}[a-z][0-9])..'
        result = [re.match(pattern, i).group(1) + " " + re.match(pattern, i).group(2)
                  for i in result if re.match(pattern, i)]

        for course in result:
            try:
                c = Course(course_code=course)
                db.session.add(c)
                db.session.commit()
            except:
                db.session.rollback()

    with open('passwords.csv', 'r') as file_in:
        result = csv.reader(file_in)
        for user in result:
            try:
                role = Role.query.filter_by(name=user[2]).first()
                new_user = User(username=str(
                    user[0]), password=user[1], role=role)
                db.session.add(new_user)
                db.session.commit()
            except:
                db.session.rollback()

    with open('enrolments.csv', 'r') as file_in:
        result = csv.reader(file_in)
        for enrolment in result:
            user = User.get_by_name(enrolment[0])
            course = enrolment[1] + " " + enrolment[2]
            user.add_course(course)
    print('Data successfully loaded into database.')


@manager.command
def test(coverage=False):
    """
    Run the unit tests.
    """

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
