#!/usr/bin/env python3
# encoding: utf-8

from threading import Thread
from .models import Answer, Survey, User, db, Course, Role
from flask import current_app
import re
import csv


class FileOperation(object):

    """
        This is the class for file operations (CSV, JSON).
    """

    @staticmethod
    def read_course():
        with open('courses.csv', 'r') as file_in:
            result = map(str, csv.reader(file_in))
            # match '["ZZZZ9999 99z9"]' like string and get the alphanumeric
            pattern = r'..([A-Z]{4}[0-9]{4})..\s.([0-9]{2}[a-z][0-9])..'
            # print([i for i in result])

            result = [re.match(pattern, i).group(1) + " " + re.match(pattern, i).group(2)
                      for i in result if re.match(pattern, i)]
            return result

    @staticmethod
    def write_flatfile_async(id):
        app = current_app._get_current_object()
        thr = Thread(target=FileOperation.write_flatfile, args=[id, app])
        thr.start()
        return thr

    @staticmethod
    def write_flatfile(id, app):
        with app.app_context():
            survey = Survey.get_by_id(id)
            answers = Answer.query.filter_by(survey_id=id).all()
            with open(str(survey.id) + '.csv', 'w') as csv_file:
                writer = csv.writer(csv_file)
                for answer in answers:
                    try:
                        if answer.owner.role.name == 'guest':
                            username = 'guest'
                        else:
                            username = "Anoymous Student"
                    except AttributeError:
                        username = "Anonymous"
                    dic = {question.description: answer.content for question, answer in zip(
                        survey.questions.all(), answer.entities.all())}
                    writer.writerow(
                        [survey.description, username, dic])

    @staticmethod
    def load_users():
        print('load start')
        app = current_app._get_current_object()
        thr = Thread(target=FileOperation.load_users_async, args=[app])
        thr.start()
        return thr

    @staticmethod
    def load_users_async(app):
        with app.app_context():
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
            print('done')
