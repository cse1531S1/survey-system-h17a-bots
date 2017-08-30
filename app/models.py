#!/usr/bin/env python3
# encoding: utf-8

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from .import db, login_manager
from datetime import datetime

"""
the database model will be demonstrated as a DRM diagram
so there won't be any comment
"""


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    last_login = db.Column(db.DateTime(), default=datetime.utcnow)
    surveys = db.relationship('Survey', backref='owner', lazy='dynamic')
    questions = db.relationship('Question', backref='owner', lazy='dynamic')
    answers = db.relationship(
        'Answer_of_Survey', backref='owner', lazy='dynamic')

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


class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.Integer, primary_key=True)


    description = db.Column(db.String(512))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course = db.Column(db.String(32))
    active = db.Column(db.Boolean())
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    questions = db.relationship('Question', secondary=Survey_Question, backref=db.backref(
        'surveys', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Survey {} belongs to {}>'.format(self.id, self.owner_id)


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.String(512))

    # q_type : question type
    # 1 : multiple choices
    q_type = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Question {}>'.format(self.id)


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    content = db.Column(db.String(512))
    rep_id = db.Column(db.Integer, db.ForeignKey('answer_of_survey.id'))

    def __repr__(self):
        return '<Answer {} for Question {}>'.format(
            self.id, self.question_id)


class Answer_of_Survey(db.Model):
    __tablename__ = 'answer_of_survey'
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'))
    answers = db.relationship('Answer', backref='rep', lazy='dynamic')

    def __repr__(self):
        return '<Answer_of_Survey {} given by {} Survey {}>'.format(
            self.id, self.owner_id, self.survey_id)
