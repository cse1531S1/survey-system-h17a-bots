#!/usr/bin/env python3
# encoding: utf-8

from flask import request, redirect, render_template, url_for, flash
from flask_login import login_required, current_user
from ..models import Survey, Question, Answer, Answer_rep
from .. import db
from . import main
import builtins


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
        flash("Questions have been successfully added to the survey")
        return redirect(url_for('.index'))

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
        flash("The question is successfully created")
        return redirect(url_for('.create_question'))

    return render_template('create_question.html')


@main.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        survey_name = request.form['title']
        survey = Survey(description=survey_name, owner_id=current_user.id)
        db.session.add(survey)
        db.session.commit()
        flash("The survey is successfully created, Please add questions to the survey now.")
        return redirect(url_for('.select_questions', survey_id=survey.id))

    return render_template('create_survey.html')


@main.route('/answer/<int:id>', methods=['GET', 'POST'])
def answer(id):
    survey = Survey.query.filter_by(id=id).first()
    questions = survey.questions.all()

    if request.method == 'POST':
        answer_rep = Answer_rep(survey_id=survey.id, owner_id=current_user.id)
        db.session.add(answer_rep)
        db.session.commit()

        datas = request.form.getlist('answer')
        print(datas)
        for data, question in zip(datas, questions):
            new_answer = Answer(rep_id=answer_rep.id,
                                question_id=question.id, content=data)
            db.session.add(new_answer)

        db.session.commit()
        flash('You successfully submit your response')
        return redirect(url_for('.index'))
    return render_template('answer_survey.html', survey=survey)


@main.route('/question_pool', methods=['GET', 'POST'])
@login_required
def question_pool():
    questions = Question.query.all()
    return render_template('question_pool.html', questions=questions)


@main.route('/delete_question/<int:id>', methods=['GET', 'POST'])
def delete_question(id):
    question_to_delete = Question.query.filter_by(id=id).first()

    if request.method == 'POST':
        if current_user.id != question_to_delete.owner_id:
            if current_user.is_admin is not True:
                flash("You don't have the permission to delete this question")
                return redirect(url_for('.question_pool'))

        if question_to_delete.surveys.first() is not None:
            flash("The question is already in use, can't delete")
            return redirect(url_for('.question_pool'))

        db.session.delete(question_to_delete)
        db.session.commit()
        flash("Delete the question successfully")
        return redirect(url_for('.question_pool'))

    return render_template('delete_question.html', question=question_to_delete)


@main.route('/delete_survey/<int:id>', methods=['GET', 'POST'])
def delete_survey(id):
    survey_to_delete = Survey.query.filter_by(id=id).first()
    answer_reps_to_delete = Answer_rep.query.filter_by(survey_id=id).all()

    if request.method == 'POST':
        if current_user.id != survey_to_delete.owner_id:
            if current_user.is_admin is not True:
                flash("You don't have the permission to delete this question")
                return redirect(url_for('.question_pool'))

        for answer_rep in answer_reps_to_delete:
            for answer in answer_rep.answers.all():
                db.session.delete(answer)
            db.session.delete(answer_rep)

        db.session.delete(survey_to_delete)
        db.session.commit()
        flash("Delete the survey successfully")
        return redirect(url_for('.index'))

    return render_template('delete_survey.html', survey=survey_to_delete)


@main.route('/survey/<int:id>', methods=['GET'])
@login_required
def survey(id):

    survey = Survey.query.filter_by(id=id).first_or_404()
    answer_reps = Answer_rep.query.filter_by(survey_id=id).all()
    for rep in answer_reps:
        print(rep.answers.all())
    # print(answer_reps)

    return render_template('survey_details.html', survey=survey, answer_reps=answer_reps, zip=builtins.zip)
