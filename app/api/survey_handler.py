#!/usr/bin/env python3
# encoding: utf-8

from flask import request, jsonify, g
from . import api
from ..models import Survey, Answer, Question, Choice, db, Course, User, Role
from ..flatfile import FileOperation
from datetime import datetime
from .authentication import auth
import collections


@api.route('/fetch_piechart', methods=['GET', 'POST'])
@auth.login_required
def fetch_pie_chart():
    data = request.get_json()
    survey_id = int(data['survey'])
    question_id = int(data['question'])
    answers = Answer.query.filter_by(survey_id=survey_id).all()
    question = Question.get_by_id(question_id)

    def make_counter(counter):
        rtn = []
        for key, value in counter.items():
            rtn.append({'name': key, 'value': value})

        return rtn

    rst = []
    for answer in answers:
        for entity in answer.entities.all():
            if entity.question_id == question.id:
                rst.append(entity.content)

    counter = dict(collections.Counter(rst))

    rtn = {
        "legend": rst,
        "data": make_counter(counter),
        "success": True,
        "title": question.description
    }
    return jsonify(rtn)


@api.route('/fetch_answer', methods=['POST', 'GET'])
@auth.login_required
def fetch_answer():
    data = request.get_json()
    id = data['id']
    answers = Answer.get_by_survey_id(id)
    nq = len(Survey.get_by_id(id).questions.all())

    if not g.current_user.is_admin() and Survey.get_by_id(id).status != 'closed':
        return jsonify({
            'message': 'This survey is not closed, don\'t hack boi.',
            'success': False
        })

    try:
        order = request.args['sort']
        if(order == '-id'):
            answers = answers[::-1]
    except:
        pass

    try:
        limit = int(request.args['limit'])
        start = (int(request.args['page']) - 1)
        answers = answers[start * limit:(start + 1) * limit]
    except:
        pass

    def to_dic(answer):
        return {
            'id': answer.id,
            'name': 'Anonymous',
            'time': answer.timestamp,
            'answers': [
                {'question': Question.get_by_id(
                    entity.question_id).description, 'answer': entity.content}
                for entity in answer.entities.all()]
        }

    rtn = []
    rtn = [to_dic(a) for a in answers]

    survey = Survey.get_by_id(id)
    qus = [i.id for i in survey.questions.all()]

    return jsonify({
        'items': rtn,
        'count': len(answers),
        'nquestion': nq,
        'questions': qus,
        'success': True
    })


@api.route('/fetch_all_survey', methods=['GET'])
@auth.login_required
def fetch_all_survey():
    def filter_end_time(surveys):
        for survey in surveys:
            time_format = '%Y-%m-%d %H:%M:%S'
            if not datetime.strptime(survey.end_date, time_format) > datetime.now():
                survey.status = 'closed'
                db.session.add(survey)
                db.session.commit()

    user = g.current_user
    role = user.role.name

    if role == 'admin':
        surveys = Survey.get_all()
    else:
        surveys = []
        courses = user.courses.all()
        for course in courses:
            to_append = course.survey
            #  Survey.query.filter_by(course=course.course_code).first()
            if to_append is not None:
                surveys.append(to_append)

    if role == 'student':
        surveys = [i for i in surveys if i.status != 'review']
    if role == 'staff':
        surveys = [i for i in surveys if i.status ==
                   'review' or i.status == 'closed']

    filter_end_time(surveys)
    total = len(surveys)

    try:
        order = request.args['sort']
        if(order == '-id'):
            surveys = surveys[::-1]
    except:
        pass

    try:
        limit = int(request.args['limit'])
        start = int(request.args['page']) - 1
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
        def process_type(type_id):
            if type_id == 1:
                return 'Multiple Choices'
            if type_id == 2:
                return 'Text Based Question'
        return {
            'id': survey.id,
            'title': survey.description,
            'owner': survey.owner.username if survey.owner else "AnoymousUser",
            'responses': len(Answer.get_by_survey_id(survey.id)),
            'timestamp': datetime.strftime(survey.timestamp, r'%d-%m-%Y %H:%M'),
            'course': survey.get_course_code(),
            'questions_man': [{"id": q.id, "description": q.description, "type": process_type(q.q_type)}
                              for q in survey.questions.all() if q.optional is False],
            'questions_opt': [{"id": q.id, "description": q.description, "type": process_type(q.q_type)}
                              for q in survey.questions.all() if q.optional is True],
            'start_time': survey.start_date,
            'end_time': survey.end_date,
            'status': survey.status,
            'id_hash': survey.id_hash
        }

    result = [to_dict(survey) for survey in surveys]

    return jsonify({
        'total': total,
        'items': result
    })


@api.route('/fetch_course', methods=['GET', 'OPTION'])
def fetch_course():
    li = FileOperation.read_course()

    def check(course_code):
        course = Course.get_by_code(course_code)
        try:
            if course.survey_id is None:
                return True
            else:
                return False
        except:
            pass

    li = list(filter(check, li))
    return jsonify({
        'items': li
    })


@api.route('/modify_survey', methods=['GET', 'POST'])
@auth.login_required
def modify_survey():
    data = request.get_json()
    survey_id = int(data['id'])
    questions = data['questions_opt'] + data['questions_man']
    questions_dump = [i['id'] for i in questions]

    survey = Survey.get_by_id(survey_id)
    if data['purpose'] != 'update_status':
        survey.remove_all_questions()
        survey.set_questions(questions_dump)
    elif data['purpose'] == 'review':
        survey.remove_optional_questions()
        survey.set_questions(questions_dump)

    survey.description = data['title']
    timestart = data['start']
    survey.start_date = timestart
    timeend = data['end']
    survey.end_date = timeend

    survey.status = data['status']
    db.session.add(survey)
    db.session.commit()
    return jsonify({
        "success": True
    })


@api.route('/user_verify', methods=['GET', 'POST'])
@auth.login_required
def verify_user():
    data = request.get_json()
    username = data['name']

    user = User.get_by_name(username)
    user.verified = data['status']

    db.session.add(user)
    db.session.commit()
    return jsonify({
        'success': True
    })


@api.route('/fetch_question', methods=['GET', 'OPTION'])
@auth.login_required
def fetch_question():
    questions = [i for i in Question.get_all() if i.deleted is not True]
    courses = Course.get_all()
    loaded = False
    if len(courses) != 0:
        loaded = True

    def to_dict(question):
        qt = question.q_type
        qtype = ""
        if qt == 1:
            qtype = "Multiple Choices"
        if qt == 2:
            qtype = 'Text Based Question'

        return {
            "type": qtype,
            "id": question.id,
            "optional": question.optional,
            "choices": [i.content for i in question.choices.all()],
            "description": question.description
        }

    result = [to_dict(question) for question in questions]
    man = []
    opt = []
    for i in result:
        if i['optional']:
            opt.append(i)
        else:
            man.append(i)

    return jsonify({
        'loaded': loaded,
        'mandatory': man,
        'optional': opt
    })


@api.route('/question_pool', methods=['GET', 'OPTION'])
@auth.login_required
def question_pool():
    questions = [i for i in Question.get_all() if i.deleted is not True]
    totalnum = len(questions)

    try:
        order = request.args['sort']
        if(order == '-id'):
            questions = questions[::-1]
    except:
        pass

    try:
        limit = int(request.args['limit'])
        start = int(request.args['page']) - 1
        questions = questions[start * limit:(start + 1) * limit]
    except:
        print('error here')

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
        elif qt == 2:
            qtype = "Text Based Question"

        # print(qtype)
        # print(qt)
        return {
            "type": qtype,
            "id": question.id,
            "optional": question.optional,
            "choices": [i.content for i in question.choices.all()],
            "title": question.description
        }

    result = [to_dict(question) for question in questions]

    return jsonify({
        'total': totalnum,
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
                           times=[timestart, timeend], course=data['course'])

    questions = data['questions_opt'] + data['questions_man']
    questions_dump = [i['id'] for i in questions]
    survey.set_questions(questions_dump)
    db.session.add(survey)
    db.session.commit()
    return jsonify({
        "success": True
    })


@api.route('/create_question', methods=['POST', 'GET'])
@auth.login_required
def create_question():
    user = g.current_user
    data = request.get_json()
    q_type = int(data['qType'])
    # print(data['qType'])
    question = Question.create(description=data['title'], owner_id=user.id,
                               q_type=q_type, optional=data['optional'])
    if q_type == 1:
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

    question_to_delete = Question.get_by_id(id)
    question_to_delete.deleted = True
    db.session.add(question_to_delete)
    db.session.commit()

    return jsonify({
        "success": True,
    })


@api.route('/srstatic', methods=['GET'])
@auth.login_required
def srstatic():
    survey_count = len(Survey.get_all())
    response_count = len(Answer.get_all())
    return jsonify({
        "success": True,
        'surveys': survey_count,
        'responses': response_count
    })


@api.route('/load_user', methods=['GET'])
@auth.login_required
def load_user():
    FileOperation.load_users()
    return jsonify({
        "success": True,
    })


@api.route('/register', methods=['GET', 'POST'])
def register():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        if User.get_by_name(username) is not None:
            return jsonify({
                'success': False,
                'message': 'this username already exists'
            })

        role = Role.get_by_name('guest')
        new = User(username=username, password=password,
                   role=role, verified=False)
        db.session.add(new)
        db.session.commit()

        for c in data['course']:
            new.add_course(c)

        return jsonify({
            'success': True,
        })
    except:
        return jsonify({
            'success': False
        })


@api.route('/user_pool', methods=['GET', 'POST'])
@auth.login_required
def guest_pool():
    users = User.query.filter_by(role=Role.get_by_name('guest')).all()
    totalnum = len(users)

    try:
        limit = int(request.args['limit'])
        start = int(request.args['page']) - 1
        users = users[start * limit:(start + 1) * limit]
    except:
        pass

    try:
        title = request.args['title']
        users = list(filter(lambda x: title.lower()
                            in x.username.lower(), users))
    except:
        pass

    def to_json(user):
        return {
            'name': user.username,
            'courses': [i.course_code for i in user.courses.all()],
            'status': 'verified' if user.verified else 'unverified',
            'success': True
        }

    return jsonify({
        'items': [to_json(i) for i in users],
        'total': totalnum
    })
