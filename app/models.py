#!/usr/bin/env python3
# encoding: utf-8

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import JSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db
from datetime import datetime
import hashlib

"""
the database model will be demonstrated as a DRM diagram
so there won't be any comment
"""


class DatabaseUtil:
    """
    This class is the class of helper functions will be inherited
    by all other database model classes
    """

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_by_owner_id(cls, id):
        return cls.query.filter_by(owner_id=id).all()

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def delete_by_id(cls, id):
        to_delete = cls.query.filter_by(id=id).first()
        db.session.delete(to_delete)
        db.session.commit()

    @classmethod
    def create(cls):
        pass


UserCourse = db.Table('user_course',
                      db.Column('user_id', db.Integer,
                                db.ForeignKey('users.id')),
                      db.Column('course_id', db.Integer,
                                db.ForeignKey('courses.id'))
                      )


class Role(db.Model, DatabaseUtil):
    """
    The role of the user.
    Currently having: admin, staff, student and guest.
    """

    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = ['admin', 'student', 'staff', 'guest']
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            db.session.add(role)
        db.session.commit()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def is_staff(self):
        return self.name == 'staff'

    def is_admin(self):
        return self.name == 'admin'


class User(db.Model, DatabaseUtil):
    """
    Each user has a role and a username for login.
    For security reason, password will be stored in hashed.
    """

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    username = db.Column(db.String(64), unique=True, index=True)
    verified = db.Column(db.Boolean, default=True)
    password_hash = db.Column(db.String(128))
    surveys = db.relationship('Survey', backref='owner', lazy='dynamic')
    questions = db.relationship('Question', backref='owner', lazy='dynamic')
    answers = db.relationship('Answer', backref='owner', lazy='dynamic')
    courses = db.relationship('Course', secondary=UserCourse, backref=db.backref(
        'users', lazy='dynamic'), lazy='dynamic')

    def generate_auth_token(self, expiration=None):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.id}).decode('ascii')

    def is_admin(self):
        return self.role.name == 'admin'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(username=name).first()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.get_by_id(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.username == 'admin':
            self.is_admin = True
        else:
            self.is_admin = False

    def add_course(self, course_code):
        course = Course.get_by_code(course_code)
        self.courses.append(course)
        db.session.add(self)
        db.session.commit()


class Course(db.Model, DatabaseUtil):
    """
    Used to store all courses.
    A survey belongs to a course.
    """

    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, index=True)
    course_code = db.Column(db.String(32), unique=True, index=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))

    @staticmethod
    def get_by_code(code):
        return Course.query.filter_by(course_code=code).first()


SurveyQuestion = db.Table('survey_question',
                          db.Column('survey_id', db.Integer,
                                    db.ForeignKey('surveys.id')),
                          db.Column('question_id', db.Integer,
                                    db.ForeignKey('questions.id'))
                          )


class Survey(db.Model, DatabaseUtil):
    """
    Hashed survey id will be used to generating survey link.
    For future development, survey should have a owner.
    Currently, all surveys belong to admin.
    """

    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True, index=True)
    id_hash = db.Column(db.String(128), index=True)
    description = db.Column(db.String(512))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course = db.relationship('Course', backref='survey', lazy='dynamic')
    status = db.Column(db.String(32))
    start_date = db.Column(db.String(64))
    end_date = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    questions = db.relationship('Question', secondary=SurveyQuestion, backref=db.backref(
        'surveys', lazy='dynamic'), lazy='dynamic')

    @staticmethod
    def get_by_hash(id):
        rtn = Survey.query.filter_by(id_hash=id).first_or_404()
        return rtn

    @classmethod
    def create(cls, description, owner_id, course, times):
        course_in_db = Course.get_by_code(course)
        new = cls(description=description, owner_id=owner_id, start_date=times[0],
                  end_date=times[1], status="review")
        db.session.add(new)
        db.session.commit()
        course_in_db.survey_id = new.id
        new.id_hash = cls.generate_id_hash(new.id)
        db.session.add(new, course_in_db)
        db.session.commit()
        return new

    def get_course_code(self):
        return self.course.first().course_code

    def set_questions(self, question_ids):
        for question_id in question_ids:
            question = Question.get_by_id(int(question_id))
            self.questions.append(question)
        db.session.add(self)
        db.session.commit()

    def remove_all_questions(self):
        for question in self.questions.all():
            self.questions.remove(question)
        db.session.add(self)
        db.session.commit()

    def remove_optional_questions(self):
        for question in self.questions.all():
            if question.optional:
                self.questions.remove(question)
        db.session.add(self)
        db.session.commit()

    def generate_id_hash(id):
        m = hashlib.sha256()
        m.update(str(id).encode('utf-8'))
        return m.hexdigest()

    def __repr__(self):
        return '<Survey {} belongs to {}>'.format(self.id, self.owner_id)


class Question(db.Model, DatabaseUtil):
    """
    Store all questions
    Deleted questions won't be shown in question pool,
    but still be used by surveys if there is one.
    """

    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    optional = db.Column(db.Boolean)
    deleted = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(512))

    """
    q_type : question type
    1 : multiple choices
    2 : text based question
    """
    q_type = db.Column(db.Integer, default=1)

    choices = db.relationship('Choice', backref='question', lazy='dynamic')

    @classmethod
    def create(cls, description, owner_id, optional, q_type=1):
        new = cls(description=description, owner_id=owner_id,
                  optional=optional, q_type=q_type)
        db.session.add(new)
        db.session.commit()
        return new

    def __repr__(self):
        return '<Question {}>'.format(self.id)


class Choice(db.Model, DatabaseUtil):
    __tablename__ = 'choices'
    id = db.Column(db.Integer, primary_key=True, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    content = db.Column(db.String(128))

    @classmethod
    def create(cls, content, question_id):
        new = cls(question_id=question_id, content=content)
        db.session.add(new)
        db.session.commit()
        return new


class Answer(db.Model, DatabaseUtil):
    """
    A set of AnswerEntity for a survey
    """

    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.now())
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))
    entities = db.relationship('AnswerEntity', backref='ans', lazy='dynamic')

    @classmethod
    def get_by_survey_id(cls, id):
        rtn = cls.query.filter_by(survey_id=id).all()
        return rtn

    @classmethod
    def check_answered(cls, id, survey_id):
        answers = cls.get_by_survey_id(survey_id)
        for answer in answers:
            if answer.owner_id == id:
                return False
        return True

    @classmethod
    def delete_by_id(cls, id):
        answer_to_delete = cls.get_by_id(id)
        for entity in answer_to_delete.entities.all():
            db.session.delete(entity)
        db.session.delete(answer_to_delete)

    @classmethod
    def delete_by_survey_id(cls, id):
        answer_to_delete = cls.get_by_survey_id(id)
        for answer in answer_to_delete:
            for entity in answer_to_delete.entities.all():
                db.session.delete(entity)
            db.session.delete(answer)

    @classmethod
    def create(cls, survey_id, owner_id):
        new = cls(survey_id=survey_id, owner_id=owner_id)
        db.session.add(new)
        db.session.commit()
        return new

    def __repr__(self):
        return '<Answer {} given by {} Survey {}>'.format(
            self.id, self.owner_id, self.survey_id)


class AnswerEntity(db.Model, DatabaseUtil):
    """
    Answer for a single question
    """

    __tablename__ = 'answer_entities'
    id = db.Column(db.Integer, primary_key=True, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    content = db.Column(db.String(512))
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))

    @classmethod
    def create(cls, answer_id, question_id, answer_content):
        new = cls(answer_id=answer_id, question_id=question_id,
                  content=answer_content)
        db.session.add(new)
        db.session.commit()
        return new

    def __repr__(self):
        return '<AnswerEntity {} for Question {}>'.format(
            self.id, self.question_id)
