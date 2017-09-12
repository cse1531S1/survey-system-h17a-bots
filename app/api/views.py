#!/usr/bin/env python3
# encoding: utf-8

from flask import render_template, redirect, request, url_for, flash, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from flask_cors import cross_origin
from . import api
from ..models import db
from ..models import User, Survey, AnswerSurveyLink, Answer, Question, Choice
from ..flatfile import FileOperation
from datetime import datetime
import collections

from functools import wraps
from flask import make_response


def allow_cross_domain(fun):
    @wraps(fun)
    def wrapper_fun(*args, **kwargs):
        rst = make_response(fun(*args, **kwargs))
        rst.headers['Access-Control-Allow-Origin'] = 'http://localhost:9527'
        rst.headers['Access-Control-Allow-Methods'] = 'OPTIONS,PUT,GET,POST,DELETE'
        allow_headers = "Referer,Accept,Origin,User-Agent"
        rst.headers['Access-Control-Allow-Headers'] = allow_headers
        return rst
    return wrapper_fun


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


@api.route('/fetch_all_survey', methods=['GET'])
def all_survey(path=None):
    surveys = Survey.get_all()
    order = request.args['sort']
    if(order == '-id'):
        surveys = surveys[::-1]
    limit = int(request.args['limit'])
    # surveys = Survey.get_all()
    start = (int(request.args['page']) - 1)
    surveys = surveys[start * limit:(start + 1) * limit]

    try:
        title = request.args['title']
        surveys = list(filter(lambda x: title in x.description, surveys))
    except:
        pass

    def to_dict(survey):
        return {
            'id': survey.id,
            'title': survey.description,
            'owner': survey.owner.username if survey.owner else "AnoymousUser",
            'responses': len(AnswerSurveyLink.get_by_survey_id(survey.id)),
            'timestamp': datetime.strftime(survey.timestamp, r'%d-%m-%Y %H:%M'),
            'course': survey.course,
            'questions': [{"id": q.id, "description": q.description} for q in survey.questions.all()],
            'start_time': survey.start_date,
            'end_time': survey.end_date,
            'status': survey.status
        }

    result = [to_dict(survey) for survey in surveys]

    return jsonify({
        'total': len(Survey.get_all()),
        'items': result
    })


@api.route('/fetch_course', methods=['GET', 'OPTION'])
def fetch_course():
    li = FileOperation.read_course()
    return jsonify({
        'items': li
    })


@api.route('/modify_survey', methods=['GET', 'POST'])
def modify_survey():
    data = request.get_json()
    survey_id = int(data['id'])
    questions = data['questions']
    questions_dump = [i['id'] for i in questions]
    survey = Survey.get_by_id(survey_id)
    survey.remove_all_questions()
    survey.set_questions(questions_dump)
    survey.description = data['title']
    if len(data['start']) == 24:
        # timestart = datetime.strptime( data['start'][0: -5], r'%Y-%m-%dT%H:%M:%S')
        pass
    timestart = data['start']
    survey.start_date = timestart

    if len(data['end']) == 24:
        # timeend = datetime.strptime(data['end'][0: -5], r'%Y-%m-%dT%H:%M:%S')
        pass
    timeend = data['end']
    survey.end_date = timeend

    survey.course = data['course']
    survey.status = data['status']
    db.session.add(survey)
    db.session.commit()
    return jsonify({
        "success": True
    })


@api.route('/fetch_question', methods=['GET', 'OPTION'])
def fetch_questions():
    questions = Question.get_all()

    def to_dict(question):
        return {"id": question.id, "description": question.description}

    result = [to_dict(question) for question in questions]
    return jsonify(result)


@api.route('/create_survey', methods=['GET', 'POST'])
def create_survey():
    data = request.get_json()
    timestart = datetime.strptime(
        data['start'][0: -5], r'%Y-%m-%dT%H:%M:%S')
    timeend = datetime.strptime(data['end'][0: -5], r'%Y-%m-%dT%H:%M:%S')
    survey = Survey.create(description=data['title'], owner_id=0,
                           times=[timestart, timeend], course=data['course'], active=True)

    questions = data['questions']
    questions_dump = [i['id'] for i in questions]
    survey.set_questions(questions_dump)
    survey.status = data['status']
    db.session.add(survey)
    db.session.commit()
    return jsonify({
        "success": True
    })
