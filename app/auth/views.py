#!/usr/bin/env python3
# encoding: utf-8

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import db
from ..models import User
from .forms import LoginForm, RegistForm, ChangePasswordForm
from .auth_util import verify_password


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            user = User.query.filter_by(username=form.username.data).first()
        else:
            user = User.query.filter_by(email=form.username.data).first()

        if user is not None and verify_password(user, form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password entered. Please try again.')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data, password=form.password.data)
        db.session.add(user)
        flash('You are able to login now.')
        db.session.commit()
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('main.index'))


@auth.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if verify_password(current_user, form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password entered.')
    return render_template("auth/change_password.html", form=form)
