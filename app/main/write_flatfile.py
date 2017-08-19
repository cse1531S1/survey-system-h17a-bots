#!/usr/bin/env python3
# encoding: utf-8

from threading import Thread
from ..models import Answer_of_Survey, Survey
from flask import current_app
import csv


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


def write_flatfile_async(id):
    app = current_app._get_current_object()
    thr = Thread(target=wirte_flatfile, args=[id, app])
    thr.start()
    return thr
