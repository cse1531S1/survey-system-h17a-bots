#!/usr/bin/env python3
# encoding: utf-8

from flask import request, redirect, render_template, abort, url_for, session
from flask_login import login_required, current_user
from ..models import User, Survey, Question, Answer
from .. import db
from . import main


@main.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html')


@main.route('/user/<int:id>')
@login_required
def user(id):
    if current_user.is_admin:
        surveys = Survey.query.all()
    else:
        surveys = Survey.query.filter_by(owner_id=current_user.id)

    return render_template('user.html', surveys=surveys)


@main.route('/select_questions/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def select_questions(survey_id):
    survey = Survey.query.filter_by(id=survey_id).first()

    if current_user.id != survey.owner_id and not current_user.is_administrator():
        return redirect(url_for('.index'))

    questions = Question.query.all()

    if request.method == 'POST':
        for question in survey.questions.all():
            survey.questions.remove(question)

        datas = request.form.getlist('optionCheckboxes')
        for data in datas:
            question = Question.query.filter_by(id=int(data)).first()
            survey.questions.append(question)
        db.session.add(survey)
        return "successful"

    return render_template('select_questions.html', questions=questions)


@main.route('/create_question', methods=['GET', 'POST'])
@login_required
def create_question():
    if request.method == 'POST':
        question_description = request.form['title']
        question = Question(description=question_description,
                            owner_id=current_user.id)
        db.session.add(question)
        db.session.commit()
        print(question.id)
        return "successful"
        # return redirect(url_for('.create_question', user=current_user))

    return render_template('create_question.html')


@main.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        survey_name = request.form['title']
        survey = Survey(description=survey_name, owner_id=current_user.id)
        db.session.add(survey)
        db.session.commit()
        print(survey.id)
        return redirect(url_for('.select_questions', survey_id=survey.id))

    return render_template('create_survey.html')


@main.route('/answer/<int:id>', methods=['GET', 'POST'])
def answer(id):
    survey = Survey.query.filter_by(id=id).first()
    questions = survey.questions.all()

    if request.method == 'POST':
        datas = request.form.getlist('answer')
        print(datas)
        for data, question in zip(datas, questions):
            new_answer = Answer(owner_id=current_user.id,
                                question_id=question.id, survey_id=survey.id, content=data)
            db.session.add(new_answer)

        db.session.commit()
        return "successful"

    return render_template('answer_survey.html', survey=survey, questions=questions)
