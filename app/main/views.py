#!/usr/bin/env python3
# encoding: utf-8

from flask import request, redirect, render_template, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from ..models import Survey, Question, Answer, AnswerSurveyLink, Choice
from .. import db
from . import main
from .flatfile import FileOperation
from config import basedir
from datetime import datetime
import sqlalchemy
import builtins
import os


@main.route('/', methods=['GET'])
def index():
    survey_count = len(Survey.get_all())
    response_count = len(AnswerSurveyLink.get_all())
    return render_template('index.html', survey_count=survey_count, response_count=response_count)


@main.route('/user/<int:id>')
@login_required
def user(id):
    if current_user.is_admin:
        surveys = Survey.get_all()
    else:
        surveys = Survey.get_by_owner_id(current_user.id)

    return render_template('user.html', surveys=surveys)


@main.route('/survey', methods=['GET', 'POST'])
@login_required
def create_survey():
    """
        This function is the view function for creating a survey.
    """
    questions = Question.get_all()

    if request.method == 'POST':
        title = request.form['title']
        course = request.form['course']
        timerange = request.form['choose_date'].split(' - ')
        times = [datetime.strptime(i, r'%d/%m/%Y %I:%M %p') for i in timerange]
        survey = Survey.create(description=title, owner_id=current_user.id,
                               times=times, course=course, active=True)
        question_data = request.form['questions']
        if question_data:
            selected_questions = [int(i) for i in question_data.split(',')]
        else:
            selected_questions = []
        survey.set_questions(selected_questions)
        flash("The survey has been successfully created.")
        return redirect(url_for('.index'))

    courses = FileOperation.read_course()
    return render_template('create_survey.html', courses=courses,
                           questions=questions, description="",
                           selected_questions=[], selected_course=courses[0])


@main.route('/survey/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_survey(id):
    """
        This function is the view function for modifying a survey.
        @id represents the survey ID.
    """
    survey = Survey.get_by_id(id)

    if current_user.id != survey.owner_id and not current_user.is_administrator():
        flash("You don't have sufficient permissions to modify this survey.")
        return redirect(url_for('.index'))

    questions = Question.get_all()

    if request.method == 'POST':
        title = request.form['title']
        course = request.form['course']
        Survey.delete_by_id(id)
        timerange = request.form['choose_date'].split(' - ')
        times = [datetime.strptime(i, r'%d/%m/%Y %I:%M %p') for i in timerange]
        survey = Survey.create(description=title, owner_id=current_user.id,
                               times=times, course=course, active=True)
        question_data = request.form['questions']
        if question_data:
            selected_questions = [int(i) for i in question_data.split(',')]
        else:
            selected_questions = []
        survey.set_questions(selected_questions)
        flash("You have successfully modified the survey.")
        return redirect(url_for('.index'))

    courses = FileOperation.read_course()
    selected_questions = survey.questions.all()
    not_selected_questions = [
        x for x in questions if x not in selected_questions]
    time1 = datetime.strftime(survey.start_date, r'%d/%m/%Y %I:%M %p')
    time2 = datetime.strftime(survey.end_date, r'%d/%m/%Y %I:%M %p')
    times = " - ".join([time1, time2])

    return render_template('create_survey.html', questions=not_selected_questions, times=times,
                           survey=survey, courses=courses, selected_questions=selected_questions,
                           selected_course=survey.course)


@main.route('/create_question', methods=['GET', 'POST'])
@login_required
def create_question():
    if request.method == 'POST':
        question_description = request.form['title']
        q_type = int(request.form['q_type'])
        question = Question.create(description=question_description,
                                   owner_id=current_user.id, q_type=q_type)

        choices = request.form.getlist('choice')
        for choice in choices:
            Choice.create(choice, question.id)
        flash("Successfully created the question.")
        return redirect(url_for('.create_question'))

    return render_template('create_question.html')


@main.route('/answer/<hash_str>', methods=['GET', 'POST'])
def answer(hash_str):
    """
        This function is the view function for answering a survey.
        @id represents the survey ID.
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
        FileOperation.write_flatfile_async(survey.id)
        return redirect(url_for('.thankyou'))
    return render_template('answer_survey.html', survey=survey)


@main.route('/question_pool', methods=['GET', 'POST'])
@login_required
def question_pool():
    questions = Question.query.all()
    return render_template('question_pool.html', questions=questions)


@main.route('/delete_question/<int:id>', methods=['GET', 'POST'])
def delete_question(id):
    """
        This function is the view function for deleting a question.
        @id represents the question ID.
    """
    question_to_delete = Question.query.filter_by(id=id).first_or_404()

    if request.method == 'POST':
        if current_user.id != question_to_delete.owner_id and current_user.is_admin is not True:
            flash("You don't have sufficient permissions to delete this question.")
            return redirect(url_for('.question_pool'))

        if question_to_delete.surveys.first() is not None:
            flash("The question is already assigned to a survey, \
                  please unassign it first, then come back to delete it.")
            return redirect(url_for('.question_pool'))

        Question.delete_by_id(id)
        flash("The question has been successfully deleted.")
        return redirect(url_for('.question_pool'))

    return render_template('delete_question.html', question=question_to_delete)


@main.route('/delete_survey/<int:id>', methods=['GET', 'POST'])
def delete_survey(id):
    """
        This function is the view function for deleting a survey.
        @id represents the survey ID.
    """
    survey_to_delete = Survey.get_by_id(id)

    if request.method == 'POST':
        if survey_to_delete.check_permission(current_user.id) is not True:
            flash("You don't have sufficient permissions to delete this survey.")
            return redirect(url_for('.question_pool'))
        AnswerSurveyLink.delete_by_survey_id(survey_to_delete.id)
        Survey.delete_by_id(id)
        flash("The survey has been successfully deleted.")
        return redirect(url_for('.index'))

    return render_template('delete_survey.html', survey=survey_to_delete)


@main.route('/survey_detail/<int:id>', methods=['GET'])
@login_required
def survey_detail(id):
    """
        This function is the view function for the survey details page.
        @id represents the survey ID.
    """

    survey = Survey.get_by_id(id)
    FileOperation.write_flatfile_async(id)
    answer_survey_link = AnswerSurveyLink.query.filter_by(survey_id=id).all()

    return render_template('survey_details.html', survey=survey,
                           answer_survey_link=answer_survey_link, zip=builtins.zip, str=builtins.str)


@main.route('/public_result/<hash_str>', methods=['GET'])
@login_required
def public_result(hash_str):
    """
        This function is the view function for survey details page.
        @id represents the survey ID.
    """

    survey = Survey.get_by_hash(hash_str)

    return render_template('public_survey_result.html', survey=survey)


@main.route('/survey_save/<int:id>')
@login_required
def survey_save(id):
    FileOperation.write_flatfile_async(id)
    flash("The survey results have been successfully written to a CSV file.")
    return redirect(url_for('.survey_detail', id=id))


@login_required
@main.route('/download/<filename>')
def download_csv(filename):
    path = os.path.join(basedir)
    return send_from_directory(path, filename)


@main.route('/thankyou')
def thankyou():
    """
        This function is the view function for the thank you page the respondent will see after survey completion.
    """
    return render_template('thank_you.html')


@login_required
@main.route('/dashboard')
def dashboard():
    surveys = Survey.get_all()
    return render_template('dashboard.html', surveys=surveys)
