#!/usr/bin/env python3
# encoding: utf-8

from threading import Thread
from ..models import Answer_of_Survey, Survey
from flask import current_app
import re
import csv


class file_operation(object):

    """
    this is the class for file operation
    """

    @staticmethod
    def read_course():
        with open('courses.csv', 'r') as file_in:
            result = map(str, csv.reader(file_in))
            # match "ZZZZ9999 99z9" like string
            pattern = r'..([A-Z]{4}[0-9]{4}\s[0-9]{2}[a-z][0-9])..'
            result = [re.match(pattern, i).group(1)
                      for i in result if re.match(pattern, i)]
            return result

    @staticmethod
    def write_flatfile_async(id):
        app = current_app._get_current_object()
        thr = Thread(target=wirte_flatfile, args=[id, app])
        thr.start()
        return thr


def wirte_flatfile(id, app):
    with app.app_context():
        survey = Survey.query.filter_by(id=id).first_or_404()
        answer_of_survey = Answer_of_Survey.query.filter_by(survey_id=id).all()
        with open(str(survey.id) + '.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            for an_answer_of_survey in answer_of_survey:
                username = an_answer_of_survey.owner.username
                dic = {question.description: answer.content for question in survey.questions.all()
                       for answer in an_answer_of_survey.answers.all()}
                # print(dic)
                writer.writerow(
                    [survey.description, username, dic])
