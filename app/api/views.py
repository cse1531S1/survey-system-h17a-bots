#!/usr/bin/env python3
# encoding: utf-8

from flask import render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import api
from ..models import db
from ..models import User, Survey, AnswerSurveyLink, Answer, Question


@api.route('/get_answer_data/type1/<int:survey_id>/<int:question_id>', methods=['GET', 'POST'])
def get_answer_data(survey_id, question_id):
    answer_survey_link = AnswerSurveyLink.query.filter_by(
        survey_id=survey_id).all()
    question = Question.get_by_id(question_id)
    vsa = {'label': 'Very Strongly Agree', 'value': 0}
    sa = {'label': 'Strongly Agree', 'value': 0}
    a = {'label': 'Agree', 'value': 0}
    d = {'label': 'Disagre', 'value': 0}
    sd = {'label': 'Strongly Disagree', 'value': 0}
    vsd = {'label': 'Very Strongly Disgree', 'value': 0}
    for link in answer_survey_link:
        for answer in link.answers.all():
            if answer.question_id == question.id:
                if answer.content == "Very Strongly Agree":
                    vsa['value'] += 1
                elif answer.content == "Strongly Agree":
                    sa['value'] += 1
                elif answer.content == "Agree":
                    a['value'] += 1
                elif answer.content == "Disagree":
                    d['value'] += 1
                elif answer.content == "Strongly Disagree":
                    sd['value'] += 1
                elif answer.content == "Very Strongly Disagree":
                    vsd['value'] += 1

    rtn = {
        "result": [vsa, sa, a, d, sd, vsd],
        "success": True
    }
    return jsonify(rtn)
