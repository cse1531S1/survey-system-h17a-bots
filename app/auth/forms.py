#!/usr/bin/env python3
# encoding: utf-8

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, EqualTo, Email
from ..models import User

"""
    These forms are used in the account management panel and login/registration page.
"""

class LoginForm(Form):
    username = StringField('Username/Email', validators=[
        Required(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistForm(Form):
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email("Please enter your email address.")])
    password = PasswordField('Password', validators=[Required(), EqualTo(
        'password_confirm', message='The passwords must match.')])
    password_confirm = PasswordField(
        'Please confirm your password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has already been registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username has already been registered.')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    new_password = PasswordField('New password', validators=[Required(), EqualTo(
        'password_confirm', message='The passwords must match.')])
    password_confirm = PasswordField(
        'New password confirmation', validators=[Required()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password_confirm', message='Passwords must match')])
    password_confirm = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
