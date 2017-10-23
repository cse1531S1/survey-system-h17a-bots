import unittest
import json
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role, Course, Survey, Question, Answer, AnswerEntity


class SystemTestCase(unittest.TestCase):
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

    def test_core_database_functionality(self):
        # admin_create_survey
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
                        .first().status == 'review')
        question1 = Question.create(
            description="a test question1", owner_id=user.id, optional=False, q_type=2)
        question2 = Question.create(
            description="a test question2", owner_id=user.id, optional=True, q_type=2)
        self.assertTrue(question1 is not None)
        self.assertTrue(question2 is not None)
        survey.set_questions([question1.id, question2.id])
        self.assertTrue(survey.questions.all() is not None)

        # staff_review_survey
        role = Role.get_by_name('staff')
        self.assertTrue(role is not None)
        user = User(username='staff', role=role, password='cat')
        db.session.add(user)
        db.session.commit()
        self.assertTrue(User.query.filter_by(username='staff')
                        .first() is not None)
        survey = Survey.query.filter_by(description='blah test').first()
        self.assertTrue(survey is not None)
        self.assertTrue(survey.status == 'review')
        survey.status = 'open'
        self.assertTrue(survey.status == 'open')
        db.session.add(survey)
        db.session.commit()

        # student_answer_survey
        role = Role.get_by_name('student')
        self.assertTrue(role is not None)
        user = User(username='student', role=role, password='cat')
        db.session.add(user)
        db.session.commit()
        survey = Survey.query.filter_by(description='blah test').first()
        self.assertTrue(survey is not None)
        self.assertTrue(survey.status == 'open')
        a = Answer.create(survey_id=survey.id, owner_id=user.id)
        self.assertTrue(a is not None)
        self.assertTrue(a.survey_id == survey.id)
        self.assertTrue(a.owner_id == user.id)
        for question in survey.questions.all():
            ae = AnswerEntity.create(answer_id=a.id,
                                     question_id=question.id,
                                     answer_content='blah'
                                     )
            self.assertTrue(ae is not None)
            self.assertTrue(ae.question_id == question.id)
            self.assertTrue(ae.answer_id == a.id)

        # admin_close_survey
        user = User.query.filter_by(username='admin').first()
        self.assertTrue(user is not None)
        survey = Survey.query.filter_by(description='blah test').first()
        self.assertTrue(survey is not None)
        survey.status = 'closed'
        db.session.add(survey)
        db.session.commit()
        self.assertTrue(survey.status == 'closed')

    def test_core_api_functionality(self):
        print('')
        print('Trying to create users...')
        # insert admin staff guest student and a course
        role_student = Role.get_by_name('student')
        self.assertTrue(role_student is not None)
        role_admin = Role.get_by_name('admin')
        self.assertTrue(role_admin is not None)
        role_staff = Role.get_by_name('staff')
        self.assertTrue(role_staff is not None)
        role_guest = Role.get_by_name('guest')
        self.assertTrue(role_guest is not None)
        print('Creating student...')
        student = User(username='student', role=role_student, password='cat')
        self.assertTrue(student is not None)
        print('Student successfully created.')
        print('Creating administrator...')
        admin = User(username='admin', role=role_admin, password='cat')
        self.assertTrue(admin is not None)
        print('Administrator successfully created.')
        print('Creating staff member...')
        staff = User(username='staff', role=role_staff, password='cat')
        self.assertTrue(staff is not None)
        print('Staff member successfully created.')
        print('Creating guest user...')
        guest = User(username='guest', role=role_guest,
                     password='cat', verified=True)
        self.assertTrue(guest is not None)
        print('Guest user successfully created.')
        print('Assigning courses to users...')
        course = Course(course_code='COMP2511 17s2')
        db.session.add(course)
        db.session.commit()
        code = course.course_code
        admin.add_course(code)
        student.add_course(code)
        staff.add_course(code)
        guest.add_course(code)
        self.assertTrue(course is not None)
        print('Courses successfully assigned.')
        print('Users successfully created.')

        print('')
        print('Trying to login as an administrator...')
        # login admin and get token
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('admin', 'cat'),
            data=self.get_api_data('admin', 'cat')
        )

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        admin_token = json_response['token']
        print('Successfully logged in as an administrator.')

        print('')
        print('Trying to create a mandatory question as an administrator...')
        # admin create mandatory question
        response = self.client.get(
            url_for('api.create_question'),
            headers=self.get_api_headers('admin', 'cat'),
            data=json.dumps({
                'qType': 2,
                'title': 'test question',
                'optional': False
            })
        )

        q1 = Question.query.filter_by(description='test question').first()
        self.assertTrue(q1 is not None)
        print('Successfully created a mandatory question as an administrator.')


        print('')
        print('Trying to create an optional question as an administrator...')
        # admin create optional question
        response = self.client.get(
            url_for('api.create_question'),
            headers=self.get_api_headers('admin', 'cat'),
            data=json.dumps({
                'qType': 2,
                'title': 'test optional question',
                'optional': True
            })
        )
        q2 = Question.query.filter_by(
            description='test optional question').first()
        self.assertTrue(q2 is not None)
        print('Successfully created an optional question as an administrator.')

        print('')
        print('Trying to create a survey as an administrator...')
        # admin create survey
        response = self.client.post(
            url_for('api.create_survey'),
            headers=self.get_api_headers(admin_token, ''),
            data=json.dumps({
                'start': '2017-10-23T03:17:55.000Z',
                'end': '2017-11-29T03:17:55.000Z',
                'title': 'test',
                'course': 'COMP2511 17s2',
                'questions_opt': [{'id': q2.id}],
                'questions_man': [{'id': q1.id}],
            })
        )
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['success'] is True)
        survey = Survey.query.all()[0]
        self.assertTrue(survey is not None)
        self.assertTrue(survey.status == 'review')
        print('Successfully created a survey as an administrator.')

        print('')
        print('Trying to review a survey as a staff member...')
        # staff review survey
        # login staff and get token
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('staff', 'cat'),
            data=self.get_api_data('staff', 'cat')
        )
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        staff_token = json_response['token']

        # send modify survey request
        response = self.client.post(
            url_for('api.modify_survey'),
            headers=self.get_api_headers(staff_token, ''),
            data=json.dumps({
                'id': survey.id,
                'start': survey.start_date,
                'end': survey.end_date,
                'title': 'test',
                'purpose': 'review',
                'course': 'COMP2511 17s2',
                'status': 'open',
                'questions_opt': [],
                'questions_man': [],
            })
        )

        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['success'] is True)
        survey = Survey.query.all()[0]
        self.assertTrue(survey is not None)
        self.assertTrue(survey.status == 'open')
        print('Successfully reviewed a survey as a staff member.')


        print('')
        print('Trying to answer a survey as a student...')
        # student answer survey
        # login student and get token
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('student', 'cat'),
            data=self.get_api_data('student', 'cat')
        )
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        student_token = json_response['token']

        # send answer survey form
        response = self.client.post(
            url_for('main.answer', hash_str=survey.id_hash) +
            '?token=' + student_token,
            headers=self.get_api_headers(student_token, ''),
            data=json.dumps({
                str(q1.id): 'q1',
                str(q1.id): 'q2'
            })
        )
        self.assertTrue(response.status_code == 302)
        self.assertTrue(Answer.query.all() is not None)
        self.assertTrue(b'thank' in response.data)
        print('Successfully answered a survey as a student.')


        print('')
        print('Trying to login as a guest...')
        response = self.client.get(
            url_for('api.get_token'),
            headers=self.get_api_headers('guest', 'cat'),
            data=self.get_api_data('guest', 'cat')
        )
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertIsNotNone(json_response.get('token'))
        guest_token = json_response['token']
        self.assertTrue(guest_token is not None)
        print('Successfully logged in as a guest.')


        print('')
        print('Trying to answer a survey as a guest...')
        response = self.client.post(
            url_for('main.answer', hash_str=survey.id_hash) +
            '?token=' + guest_token,
            headers=self.get_api_headers(student_token, ''),
            data=json.dumps({
                str(q1.id): 'q1',
                str(q1.id): 'q2'
            })
        )
        self.assertTrue(response.status_code == 302)
        self.assertTrue(Answer.query.all() is not None)
        self.assertTrue(b'thank' in response.data)
        print('Successfully answered survey as a guest.')


        print('')
        print('Trying to close a survey as an administrator...')
        # admin close the survey
        response = self.client.post(
            url_for('api.modify_survey'),
            headers=self.get_api_headers(admin_token, ''),
            data=json.dumps({
                'id': survey.id,
                'start': survey.start_date,
                'end': survey.end_date,
                'title': 'test',
                'purpose': 'update_status',
                'course': 'COMP2511 17s2',
                'status': 'closed',
                'questions_opt': [],
                'questions_man': [],
            })
        )

        survey = Survey.query.all()[0]
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['success'] is True)
        survey = Survey.query.all()[0]
        self.assertTrue(survey is not None)
        self.assertTrue(survey.status == 'closed')
        print('Successfully closed a survey as an administrator.')


        print('')
        print('Trying to answer a closed survey as a student...')
        # student answer after closed
        response = self.client.post(
            url_for('main.answer', hash_str=survey.id_hash) +
            '?token=' + student_token,
            headers=self.get_api_headers(student_token, '')
        )
        self.assertTrue(response.status_code == 302)
        self.assertTrue(b'not' in response.data)
        print('Student was shown the appropriate error message.')

        print('')
        print('Trying to generate a pie chart as a student...')
        # student get survey result
        response = self.client.post(
            url_for('api.fetch_pie_chart'),
            headers=self.get_api_headers(student_token, ''),
            data=json.dumps({
                'survey': survey.id,
                'question': q1.id
            })
        )
        self.assertTrue(response.status_code == 200)
        print('Successfully generated a pie chart as a student.')

        print('')
        print('Trying to delete a question as an administrator...')
        # admin delete question
        response = self.client.get(
            url_for('api.delete_question'),
            headers=self.get_api_headers('admin', 'cat'),
            data=json.dumps({'id': q2.id})
        )
        q2 = Question.get_by_id(q2.id)
        self.assertTrue(q2.deleted is True)
        print('Successfully deleted a question as an administrator.')
        print('')
