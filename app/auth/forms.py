#!/usr/bin/env python3
# encoding: utf-8

from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, EqualTo, Email, ValidationError
from ..models import User

"""
    These forms are used in the account management panel and login/registration page.
"""

class fa_map():
    fa_addon = {
            'username' : 'fa-user',
            'email' : 'fa-envelope-o',
            'password' : 'fa-key',
            'old_password' : 'fa-key',
            'new_password' : 'fa-key',
            'password_confirm' : 'fa-key',
            }


    class LoginForm(Form, fa_map):
        username = StringField('', validators=[Required(), Length(1, 64)],
                render_kw={"placeholder": "Username/ Email", })
        password = PasswordField('', validators=[Required()],
                render_kw={"placeholder": "Password", })
        remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistForm(Form, fa_map):
    username = StringField('', validators=[Required(), Length(1, 64)],
            render_kw={"placeholder": "Username", })
    email = StringField('', validators=[Required(), Length(1, 64),
        Email("Please enter your email address.")],
        render_kw={"placeholder": "Email", })
    password = PasswordField('', validators=[Required(), EqualTo(
        'password_confirm', message='The passwords must match.')],
        render_kw={"placeholder": "Password", })
    password_confirm = PasswordField('', validators=[Required()],
            render_kw={"placeholder": "Confirm your password", })
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email has already been registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username has already been registered.')


class ChangePasswordForm(Form, fa_map):
    old_password = PasswordField('', validators=[Required()],
            render_kw={"placeholder": "Old password", })
    new_password = PasswordField('', validators=[Required(), EqualTo(
        'password_confirm', message='The passwords must match.')],
        render_kw={"placeholder": "New password", })
    password_confirm = PasswordField('', validators=[Required()],
            render_kw={"placeholder": "Confirm your password", })
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(Form, fa_map):
    email = StringField('', validators=[Required(), Length(1, 64),
        Email()], render_kw={"placeholder": "Email", })
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form, fa_map):
    password = PasswordField('', validators=[Required(), 
        EqualTo('password_confirm', message='Passwords must match')],
        render_kw={"placeholder" : "New password",})
    password_confirm = PasswordField('', validators=[Required()],
            render_kw={"placeholder": "Confirm your password", })
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')

