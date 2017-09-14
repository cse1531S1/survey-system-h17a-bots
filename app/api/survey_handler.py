#!/usr/bin/env python3
# encoding: utf-8

from flask import request, jsonify, g
from . import api
from ..models import User, Survey, AnswerSurveyLink, Question, Choice, db
from ..flatfile import FileOperation
from datetime import datetime
from .authentication import auth
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


@api.route('/fetch_all_survey', methods=['GET'])
@auth.login_required
def all_survey():
    surveys = Survey.get_all()
    try:
        order = request.args['sort']
        if(order == '-id'):
            surveys = surveys[::-1]
    except:
        pass

    try:
        limit = int(request.args['limit'])
        start = (int(request.args['page']) - 1)
        surveys = surveys[start * limit:(start + 1) * limit]
    except:
        pass

    try:
        title = request.args['title']
        surveys = list(filter(lambda x: title.lower()
                              in x.description.lower(), surveys))
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
@auth.login_required
def fetch_course():
    li = FileOperation.read_course()
    return jsonify({
        'items': li
    })


@api.route('/modify_survey', methods=['GET', 'POST'])
@auth.login_required
def modify_survey():
    data = request.get_json()
    survey_id = int(data['id'])
    questions = data['questions']
    questions_dump = [i['id'] for i in questions]
    survey = Survey.get_by_id(survey_id)
    survey.remove_all_questions()
    survey.set_questions(questions_dump)
    survey.description = data['title']

    timestart = data['start']
    survey.start_date = timestart
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
@auth.login_required
def fetch_questions():
    print(request.headers)
    questions = Question.get_all()

    def to_dict(question):
        qt = question.q_type
        qtype = ""
        if qt == 1:
            qtype = "Multiple Choices"
        return {
            "Type": qtype,
            "id": question.id,
            "choices": [i.content for i in question.choices.all()],
            "description": question.description
        }

    result = [to_dict(question) for question in questions]
    return jsonify(result)


@api.route('/question_pool', methods=['GET', 'OPTION'])
@auth.login_required
def question_pool():
    questions = Question.get_all()

    try:
        order = request.args['sort']
        if(order == '-id'):
            questions = questions[::-1]
    except:
        pass
    try:
        limit = int(request.args['limit'])
        start = (int(request.args['page']) - 1)
        questions = questions[start * limit:(start + 1) * limit]
    except:
        pass

    try:
        title = request.args['title']
        questions = list(filter(lambda x: title.lower()
                                in x.description.lower(), questions))
    except:
        pass

    def to_dict(question):
        qt = question.q_type
        qtype = ""
        if qt == 1:
            qtype = "Multiple Choices"
        return {
            "type": qtype,
            "id": question.id,
            "choices": [i.content for i in question.choices.all()],
            "title": question.description
        }

    result = [to_dict(question) for question in questions]

    return jsonify({
        'total': len(Survey.get_all()),
        'items': result
    })


@api.route('/create_survey', methods=['GET', 'POST'])
@auth.login_required
def create_survey():
    user = g.current_user
    data = request.get_json()
    timestart = datetime.strptime(
        data['start'][0: -5], r'%Y-%m-%dT%H:%M:%S')
    timeend = datetime.strptime(data['end'][0: -5], r'%Y-%m-%dT%H:%M:%S')
    survey = Survey.create(description=data['title'], owner_id=user.id,
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


@api.route('/create_question', methods=['POST'])
@auth.login_required
def create_question():
    user = g.current_user
    data = request.get_json()
    print(data)
    question = Question.create(description=data['title'],
                               owner_id=user.id, q_type=int(data['qType']))
    choices = data['choices']
    for choice in choices:
        Choice.create(choice, question.id)
    return jsonify({
        "success": True,
    })


@api.route('/delete_question', methods=['POST', 'GET'])
@auth.login_required
def delete_question():
    data = request.get_json()
    id = data['id']
    current_user = g.current_user
    question_to_delete = Question.get_by_id(id)

    if current_user.id != question_to_delete.owner_id and current_user.is_admin is not True:
        return jsonify({
            'error': "You don't have sufficient permissions to delete this question."
        })

    if question_to_delete.surveys.first() is not None:
        return jsonify({
            'error': "The question is already assigned to a survey,\
            please unassign it first, then come back to delete it."
        })

    Question.delete_by_id(id)
    return jsonify({
        "success": True,
    })
