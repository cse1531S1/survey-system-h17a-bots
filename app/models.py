#!/usr/bin/env python3
# encoding: utf-8

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from datetime import datetime
import hashlib

"""
the database model will be demonstrated as a DRM diagram
so there won't be any comment
"""


class DatabaseUtil:
    """
    this class is the class of helper functions will be inherited
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

    @staticmethod
    def create(id):
        pass


class User(UserMixin, db.Model, DatabaseUtil):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    last_login = db.Column(db.DateTime(), default=datetime.utcnow)
    surveys = db.relationship('Survey', backref='owner', lazy='dynamic')
    questions = db.relationship('Question', backref='owner', lazy='dynamic')
    answers = db.relationship(
        'Answer_of_Survey', backref='owner', lazy='dynamic')

    # TODO User_role class
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.username == 'admin':
            self.is_admin = True
        else:
            self.is_admin = False

    def is_administrator(self):
        return self.is_admin

    def can(self):
        return self.is_admin

    def ping(self):
        self.last_login = datetime.utcnow()
        db.session.add(self)


class AnoymousUser(AnonymousUserMixin):
    id = 0
    is_admin = False
    username = 'AnoymousUser'

    def can(self):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnoymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


Survey_Question = db.Table('survey_question',
                           db.Column('survey_id', db.Integer,
                                     db.ForeignKey('surveys.id')),
                           db.Column('question_id', db.Integer,
                                     db.ForeignKey('questions.id'))
                           )


class Survey(db.Model, DatabaseUtil):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)
    id_hash = db.Column(db.String(128))

    description = db.Column(db.String(512), unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course = db.Column(db.String(32))
    active = db.Column(db.Boolean())
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    questions = db.relationship('Question', secondary=Survey_Question, backref=db.backref(
        'surveys', lazy='dynamic'), lazy='dynamic')

    @staticmethod
    def get_by_hash(id):
        rtn = Survey.query.filter_by(id_hash=id).first_or_404()
        return rtn

    @staticmethod
    def create(description, owner_id, course, active):
        new = Survey(description=description, owner_id=owner_id,
                     course=course, active=active)
        db.session.add(new)
        db.session.commit()
        new.id_hash = Survey.generate_id_hash(new.id)
        db.session.add(new)
        db.session.commit()
        return new

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

    def check_permission(self, id):
        current_user = User.get_by_id(id)
        if current_user.id != self.owner_id and current_user.is_admin is not True:
            return False
        else:
            return True

    def generate_id_hash(id):
        m = hashlib.sha256()
        m.update(str(id).encode('utf-8'))
        return m.hexdigest()

    def __repr__(self):
        return '<Survey {} belongs to {}>'.format(self.id, self.owner_id)


class Question(db.Model, DatabaseUtil):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.String(512), unique=True)

    # q_type : question type
    # 1 : multiple choices
    q_type = db.Column(db.Integer, default=1)

    @staticmethod
    def create(description, owner_id):
        new = Question(description=description, owner_id=owner_id)
        db.session.add(new)
        db.session.commit()

    def __repr__(self):
        return '<Question {}>'.format(self.id)


class Answer(db.Model, DatabaseUtil):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    content = db.Column(db.String(512))
    rep_id = db.Column(db.Integer, db.ForeignKey('answer_of_survey.id'))

    @staticmethod
    def create(answer_of_survey_id, question_id, answer_content):
        new = Answer(rep_id=answer_of_survey_id,
                     question_id=question_id, content=answer_content)
        db.session.add(new)
        db.session.commit()
        return new

    def __repr__(self):
        return '<Answer {} for Question {}>'.format(
            self.id, self.question_id)


class Answer_of_Survey(db.Model, DatabaseUtil):
    __tablename__ = 'answer_of_survey'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))
    answers = db.relationship('Answer', backref='rep', lazy='dynamic')

    @staticmethod
    def get_by_survey_id(id):
        rtn = Answer_of_Survey.query.filter_by(survey_id=id).all()
        return rtn

    @classmethod
    def delete_by_id(cls, id):
        answer_of_survey_to_delete = cls.get_by_id(id)
        for answer in answer_of_survey_to_delete.answers.all():
            db.session.delete(answer)
        db.session.delete(answer_of_survey_to_delete)

    @staticmethod
    def delete_by_survey_id(id):
        answer_of_survey_to_delete = Answer_of_Survey.get_by_survey_id(id)
        for answer_of_survey in answer_of_survey_to_delete:
            for answer in answer_of_survey.answers.all():
                db.session.delete(answer)
            db.session.delete(answer_of_survey)

    @staticmethod
    def create(survey_id, owner_id):
        new = Answer_of_Survey(survey_id=survey_id, owner_id=owner_id)
        db.session.add(new)
        db.session.commit()
        return new

    def __repr__(self):
        return '<Answer_of_Survey {} given by {} Survey {}>'.format(
            self.id, self.owner_id, self.survey_id)
