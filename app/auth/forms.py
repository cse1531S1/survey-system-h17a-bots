#!/usr/bin/env python3
# encoding: utf-8

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    username = StringField('Username', validators=[
        Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistForm(Form):
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required(), EqualTo(
        'password_confirm', message='Password must match.')])
    password_confirm = PasswordField(
        'Confirm your password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered.')
