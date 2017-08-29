#!/usr/bin/env python3
# encoding: utf-8

from flask import request, redirect, render_template, url_for, flash, abort
from flask_login import login_required, current_user
from ..models import Survey, Question, Answer, Answer_of_Survey
from .. import db
from . import main
from .flatfile import write_flatfile_async, read_course
import builtins


@main.route('/', methods=['GET'])
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


@main.route('/select_questions/<int:id>', methods=['GET', 'POST'])
@login_required
def select_questions(id):
    """
    this function is view function for choosing questions for a survey
    and is also used for modifying a survey
    @id = survey id
    """
    survey = Survey.query.filter_by(id=id).first()

    if current_user.id != survey.owner_id and not current_user.is_administrator():
        return redirect(url_for('.index'))

    questions = Question.query.all()

    if request.method == 'POST':
        for question in survey.questions.all():
            survey.questions.remove(question)

        datas = request.form.getlist('to[]')
        for data in datas:
            question = Question.query.filter_by(id=int(data)).first()
            survey.questions.append(question)
        db.session.add(survey)
        flash("Questions have been successfully added to the survey")
        return redirect(url_for('.index'))

    return render_template('select_questions.html', questions=questions)


@main.route('/modify_survey/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_survey(id):
    """
    this function is view function for choosing questions for a survey
    and is also used for modifying a survey
    @id = survey id
    """
    survey = Survey.query.filter_by(id=id).first()

    if current_user.id != survey.owner_id and not current_user.is_administrator():
        return redirect(url_for('.index'))

    questions = Question.query.all()
    questions_in_survey = survey.questions.all()

    if request.method == 'POST':
        title = request.form['title']
        survey.description = title

        for question in survey.questions.all():
            survey.questions.remove(question)

        datas = request.form.getlist('to[]')
        for data in datas:
            question = Question.query.filter_by(id=int(data)).first()
            survey.questions.append(question)
        db.session.add(survey)
        flash("You successfully modified the survey")
        return redirect(url_for('.index'))

    return render_template('modify_survey.html', questions=questions, survey=survey, questions_in_survey=questions_in_survey)


@main.route('/create_question', methods=['GET', 'POST'])
@login_required
def create_question():
    if request.method == 'POST':
        question_description = request.form['title']
        question = Question(description=question_description,
                            owner_id=current_user.id)
        db.session.add(question)
        db.session.commit()
        # print(question.id)
        flash("The question is successfully created")
        return redirect(url_for('.create_question'))

    return render_template('create_question.html')


@main.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        survey_name = request.form['title']
        course = request.form['course']
        survey = Survey(description=survey_name,
                        owner_id=current_user.id, course=course, active=True)
        db.session.add(survey)
        db.session.commit()
        flash("The survey is successfully created, Please add questions to the survey now.")
        return redirect(url_for('.select_questions', id=survey.id))

    courses = read_course()
    return render_template('create_survey.html', courses=courses)


@main.route('/answer/<int:id>', methods=['GET', 'POST'])
def answer(id):
    """
    this function is the view function for answering a survey
    @id : the id for a survey
    """
    survey = Survey.query.filter_by(id=id).first()
    if survey is None:
        abort(404)
    questions = survey.questions.all()

    if request.method == 'POST':
        answer_of_survey = Answer_of_Survey(
            survey_id=survey.id, owner_id=current_user.id)
        db.session.add(answer_of_survey)
        db.session.commit()

        datas = request.form.getlist('answer')
        # print(datas)
        for data, question in zip(datas, questions):
            new_answer = Answer(rep_id=answer_of_survey.id,
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
    """
    the functio is the view function for deleting a question
    @id : id for a question
    """
    question_to_delete = Question.query.filter_by(id=id).first()

    if request.method == 'POST':
        if current_user.id != question_to_delete.owner_id or current_user.is_admin is not True:
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
    """
    the functio is the view function for deleting a survey
    @id : id for a survey
    """
    survey_to_delete = Survey.query.filter_by(id=id).first()
    answer_of_survey_to_delete = Answer_of_Survey.query.filter_by(
        survey_id=id).all()

    if request.method == 'POST':
        if current_user.id != survey_to_delete.owner_id or current_user.is_admin is not True:
            flash("You don't have the permission to delete this survey")
            return redirect(url_for('.question_pool'))

        for answer_of_survey in answer_of_survey_to_delete:
            for answer in answer_of_survey.answers.all():
                db.session.delete(answer)
            db.session.delete(answer_of_survey)

        db.session.delete(survey_to_delete)
        db.session.commit()
        flash("Delete the survey successfully")
        return redirect(url_for('.index'))

    return render_template('delete_survey.html', survey=survey_to_delete)


@main.route('/survey/<int:id>', methods=['GET'])
@login_required
def survey_detail(id):
    """
    the function is the view function for survey detail page
    @id : the id of a survey
    """

    survey = Survey.query.filter_by(id=id).first_or_404()
    answer_of_survey = Answer_of_Survey.query.filter_by(survey_id=id).all()

    # for rep in answer_of_survey:
    # print(rep.answers.all())
    # print(answer_reps)

    return render_template('survey_details.html', survey=survey,
                           answer_of_survey=answer_of_survey, zip=builtins.zip)


@main.route('/survey_save/<int:id>')
@login_required
def survey_save(id):
    write_flatfile_async(id)
    flash("Save the survey result to csv file successfully!")
    return redirect(url_for('.survey_detail', id=id))
