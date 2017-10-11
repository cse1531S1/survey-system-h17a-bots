#!/usr/bin/env python3
# encoding: utf-8

from flask import request, redirect, render_template, url_for, flash, send_from_directory, g
from flask_login import login_required, current_user
from ..models import Survey, Question, Answer, AnswerEntity, Choice, User
from .. import db
from . import main
from ..flatfile import FileOperation
from config import basedir
from datetime import datetime
import builtins
import os


@main.route('/', methods=['GET'])
def index():
    survey_count = len(Survey.get_all())
    response_count = len(Answer.get_all())
    return render_template('index.html', survey_count=survey_count, response_count=response_count)


@main.route('/user/<int:id>')
@login_required
def user(id):
    if current_user.is_admin:
        surveys = Survey.get_all()
    else:
        surveys = Survey.get_by_owner_id(current_user.id)

    return render_template('user.html', surveys=surveys)


@login_required
@main.route('/download/<filename>')
def download_csv(filename):
    path = os.path.join(basedir)
    return send_from_directory(path, filename)


@main.route('/answer/<hash_str>', methods=['GET', 'POST'])
def answer(hash_str):
    """
        This function is the view function for answering a survey.
        @id represents the survey ID.
    """
    try:
        token = request.args['token']
        user = User.verify_auth_token(token)
    except:
        return redirect(url_for('.not_allowed'))

    if not user or user.user_role == 'staff' or user.user_role == 'admin':
        return redirect(url_for('.not_allowed'))

    survey = Survey.get_by_hash(hash_str)
    if survey.status != 'open':
        return redirect(url_for('.not_allowed'))

    # if not Answer.check_answered(user.id, survey.id):
        # return redirect(url_for('.answered'))

    if request.method == 'POST':
        questions = survey.questions.all()
        answer = Answer.create(survey_id=survey.id, owner_id=user.id)

        for question in questions:
            try:
                answer_content = request.form[str(question.id)]
                AnswerEntity.create(
                    answer_id=answer.id, question_id=question.id, answer_content=answer_content)
            except:
                pass

        db.session.commit()
        FileOperation.write_flatfile_async(survey.id)
        return redirect(url_for('.thankyou'))

    questions = survey.questions.all()
    questions_man = []
    questions_opt = []

    for i in questions:
        if i.optional:
            questions_opt.append(i)
        elif not i.optional:
            questions_man.append(i)

    return render_template('answer_survey.html', survey=survey, course=survey.get_course_code(),
                           questions_opt=questions_opt, questions_man=questions_man)


@main.route('/thankyou')
def thankyou():
    """
        This function is the view function for the thank you page the
        respondent will see after survey completion.
    """
    return render_template('thank_you.html')


@main.route('/answered')
def answered():
    return render_template('answered.html')


@main.route('/not_allowed')
def not_allowed():
    return render_template('not_allowed.html')


@login_required
@main.route('/dashboard')
def dashboard():
    surveys = Survey.get_all()
    return render_template('dashboard.html', surveys=surveys)
