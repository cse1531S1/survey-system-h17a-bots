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
    return redirect(url_for('.create_survey'))


@main.route('/select_questions/<int:survey_id>', methods=['GET', 'POST'])
@login_required
def select_questions(survey_id):
    questions = Question.query.all()
    if survey_id is None:
        return redirect(url_for('.create_survey'))

    if request.method == 'POST':
        datas = request.form.getlist('optionCheckboxes')
        survey = Survey.query.filter_by(id=survey_id).first()
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
