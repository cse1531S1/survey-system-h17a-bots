#!/usr/bin/env python3
# encoding: utf-8

from flask import request, redirect, render_template, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from ..models import Survey, Question, Answer, AnswerSurveyLink
from .. import db
from . import main
from .flatfile import FileOperation
from config import basedir
import builtins
import os


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route('/user/<int:id>')
@login_required
def user(id):
    if current_user.is_admin:
        surveys = Survey.get_all()
    else:
        surveys = Survey.get_by_owner_id(current_user.id)

    return render_template('user.html', surveys=surveys)


@main.route('/select_questions/<int:id>', methods=['GET', 'POST'])
@login_required
def select_questions(id):
    """
    this function is view function for choosing questions for a survey
    and is also used for modifying a survey
    @id = survey id
    """
    survey = Survey.get_by_id(id)

    if current_user.id != survey.owner_id and not current_user.is_administrator():
        return redirect(url_for('.index'))

    questions = Question.get_all()

    if request.method == 'POST':
        survey.remove_all_questions()
        selected = request.form.getlist('to[]')
        survey.set_questions(selected)
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
    survey = Survey.get_by_id(id)

    if current_user.id != survey.owner_id and not current_user.is_administrator():
        return redirect(url_for('.index'))

    questions = Question.get_all()

    if request.method == 'POST':
        title = request.form['title']
        survey.description = title
        survey.remove_all_questions()
        selected = request.form.getlist('to[]')
        survey.set_questions(selected)
        flash("You successfully modified the survey")
        return redirect(url_for('.index'))

    return render_template('modify_survey.html', questions=questions,
                           survey=survey)


@main.route('/create_question', methods=['GET', 'POST'])
@login_required
def create_question():
    if request.method == 'POST':
        question_description = request.form['title']
        Question.create(description=question_description,
                        owner_id=current_user.id)
        flash("The question is successfully created")
        return redirect(url_for('.create_question'))

    return render_template('create_question.html')


@main.route('/create_survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    if request.method == 'POST':
        survey_name = request.form['title']
        course = request.form['course']
        survey = Survey.create(description=survey_name,
                               owner_id=current_user.id, course=course, active=True)
        flash("The survey is successfully created, Please add questions to the survey now.")
        return redirect(url_for('.select_questions', id=survey.id))

    courses = file_operation.read_course()
    return render_template('create_survey.html', courses=courses)


@main.route('/answer/<hash_str>', methods=['GET', 'POST'])
def answer(hash_str):
    """
    this function is the view function for answering a survey
    @id : the id for a survey
    """
    survey = Survey.get_by_hash(hash_str)

    if request.method == 'POST':
        questions = survey.questions.all()
        answer_survey_link = AnswerSurveyLink.create(
            survey_id=survey.id, owner_id=current_user.id)

        for question in questions:
            answer_content = request.form[str(question.id)]
            Answer.create(answer_survey_link_id=answer_survey_link.id,
                          question_id=question.id, answer_content=answer_content)

        db.session.commit()
        file_operation.write_flatfile_async(survey.id)
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
    question_to_delete = Question.query.filter_by(id=id).first_or_404()

    if request.method == 'POST':
        if current_user.id != question_to_delete.owner_id and current_user.is_admin is not True:
            flash("You don't have the permission to delete this question")
            return redirect(url_for('.question_pool'))

        if question_to_delete.surveys.first() is not None:
            flash("The question is already in use, can't delete")
            return redirect(url_for('.question_pool'))

        Question.delete_by_id(id)
        flash("Delete the question successfully")
        return redirect(url_for('.question_pool'))

    return render_template('delete_question.html', question=question_to_delete)


@main.route('/delete_survey/<int:id>', methods=['GET', 'POST'])
def delete_survey(id):
    """
    the functio is the view function for deleting a survey
    @id : id for a survey
    """
    survey_to_delete = Survey.get_by_id(id)

    if request.method == 'POST':
        if survey_to_delete.check_permission(current_user.id) is not True:
            flash("You don't have the permission to delete this survey")
            return redirect(url_for('.question_pool'))
        AnswerSurveyLink.delete_by_survey_id(survey_to_delete.id)
        Survey.delete_by_id(id)
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

    survey = Survey.get_by_id(id)
    file_operation.write_flatfile_async(id)
    answer_survey_link = AnswerSurveyLink.query.filter_by(survey_id=id).all()

    return render_template('survey_details.html', survey=survey,
                           answer_survey_link=answer_survey_link, zip=builtins.zip, str=builtins.str)


@main.route('/survey_save/<int:id>')
@login_required
def survey_save(id):
    file_operation.write_flatfile_async(id)
    flash("Save the survey result to csv file successfully!")
    return redirect(url_for('.survey_detail', id=id))


@login_required
@main.route('/download/<filename>')
def download_csv(filename):
    path = os.path.join(basedir)
    return send_from_directory(path, filename)
