#!/usr/bin/env python3
# encoding: utf-8

from flask import render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import api
from ..models import db
from ..models import User, Survey, AnswerSurveyLink, Answer, Question, Choice
import collections


@api.route('/get_answer_data/type1/<int:survey_id>/<int:question_id>', methods=['GET', 'POST'])
def get_answer_data(survey_id, question_id):
    answer_survey_link = AnswerSurveyLink.query.filter_by(
        survey_id=survey_id).all()
    question = Question.get_by_id(question_id)

    def make_counter(counter):
        rtn = []
        for key, value in counter.items():
            rtn.append({'label': key, 'value': value})

        return rtn

    rst = []
    for link in answer_survey_link:
        for answer in link.answers.all():
            if answer.question_id == question.id:
                rst.append(answer.content)

    counter = dict(collections.Counter(rst))

    rtn = {
        "result": make_counter(counter),
        "success": True
    }
    return jsonify(rtn)


@api.route('/create_question', methods=['POST'])
def create_question():
    question_description = request.form['title']
    q_type = int(request.form['q_type'])
    question = Question.create(description=question_description,
                               owner_id=current_user.id, q_type=q_type)

    choices = request.form.getlist('choice')
    for choice in choices:
        Choice.create(choice, question.id)
    return jsonify({
        "success": True,
    })
