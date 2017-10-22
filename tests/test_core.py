import unittest
import json
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Course, Survey, Question, Answer, AnswerEntity


class CoreTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_api_data(self, username, password):
        return json.dumps({'username': username, 'password': password})

    def functionality_test(self):

        def admin_create_survey():
            role = Role.get_by_name('admin')
            self.assertTrue(role is not None)
            user = User(username='admin', role=role, password='cat')
            db.session.add(user)
            db.session.commit()
            self.assertTrue(User.query.filter_by(
                username='admin').first() is not None)

            c = Course(course_code='TEST')
            db.session.add(c)
            db.session.commit()
            self.assertTrue(Course.query.filter_by(
                course_code='TEST').first() is not None)
            survey = Survey.create(description='blah test', times=['1', '2'],
                                   owner_id=user.id, course=c.course_code)
            self.assertTrue(Survey.query.filter_by(description='blah test')
                            .first() is not None)
            self.assertTrue(Survey.query.filter_by(description='blah test')
                            .first().status is 'review')
            question1 = Question.create(
                description="a test question1", owner_id=user.id, optional=False, q_type=2)
            question2 = Question.create(
                description="a test question2", owner_id=user.id, optional=True, q_type=2)
            self.assertTrue(question1 is not None)
            self.assertTrue(question2 is not None)
            survey.set_questions([question1.id, question2.id])
            self.assertTrue(survey.questions.all() is not None)

        def staff_review_survey():
            role = Role.get_by_name('staff')
            self.assertTrue(role is not None)
            user = User(username='staff', role=role, password='cat')
            db.session.add(user)
            db.session.commit()
            self.assertTrue(User.query.filter_by(username='staff')
                            .first() is not None)
            survey = Survey.query.filter_by(description='blah test').first()
            self.assertTrue(survey is not None)
            self.asserttrue(survey.status is 'review')
            survey.status = 'open'
            self.assertTrue(survey.status is 'open')
            db.session.add(survey)
            db.session.commit()

        def student_answer_survey():
            role = Role.get_by_name('student')
            self.assertTrue(role is not None)
            user = User(username='student', role=role, password='cat')
            db.session.add(user)
            db.session.commit()
            survey = Survey.filter_by(description='blah test').first()
            self.assertTrue(survey is not None)
            self.assertTrue(survey.status is 'open')
            a = Answer.create(survey_id=survey.id, owner_id=user.id)
            self.assertTrue(a is not None)
            self.assertTrue(a.survey_id is survey.id)
            self.assertTrue(a.owner_id is user.id)
            for question in survey.questions.all():
                ae = AnswerEntity.create(answer_id=a.id,
                                         question_id=question.id,
                                         answer_content='blah'
                                         )
                self.assertTrue(ae is not None)
                self.assertTrue(ae.question_id is question.id)
                self.assertTrue(ae.answer_id is a.id)

        def admin_close_survey():
            user = User.filter_by(username='admin').first()
            self.assertTrue(user is not None)
            survey = Survey.filter_by(description='blah test').first()
            self.assertTrue(survey is not None)
            survey.status = 'closed'
            db.session.add(survey)
            db.session.commit()
            self.assertTrue(survey.status is 'closed')

        admin_create_survey()
        staff_review_survey()
        student_answer_survey()
        admin_close_survey()
