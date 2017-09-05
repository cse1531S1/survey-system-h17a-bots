#!/usr/bin/env python3
# encoding: utf-8

from threading import Thread
from ..models import AnswerSurveyLink, Survey
from flask import current_app
import re
import csv


class FileOperation(object):

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
        thr = Thread(target=FileOperation.write_flatfile, args=[id, app])
        thr.start()
        return thr

    @staticmethod
    def write_flatfile(id, app):
        with app.app_context():
            survey = Survey.get_by_id(id)
            answer_survey_links = AnswerSurveyLink.query.filter_by(
                survey_id=id).all()
            with open(str(survey.id) + '.csv', 'w') as csv_file:
                writer = csv.writer(csv_file)
                for link in answer_survey_links:
                    try:
                        username = link.owner.username
                    except AttributeError:
                        username = "Anonymous"
                    dic = {question.description: answer.content for question, answer in zip(
                        survey.questions.all(), link.answers.all())}
                    print(dic)
                    writer.writerow(
                        [survey.description, username, dic])
