from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import secrets

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username= username).first()
            if user:
                salt_user = user.password[-64:]
                password += salt_user
                if check_password_hash(user.password[:-64], password):
                    flash('Logged in successfully!', category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Username does not exist.', category='error')
    
    except Exception as e:
        return render_template("error.html", user=current_user)


    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            name = request.form.get('name')
            username = request.form.get('username')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')

            user = User.query.filter_by(username=username).first()
            email_exists = User.query.filter_by(email=email).first()

            if user:
                flash('Username already exists.', category='error')
            elif email_exists:
                flash('Email already exists.', category='error')
            elif len(username) < 4:
                flash('Username must be greater than 3 characters.', category='error')
            elif len(name) < 2:
                flash('Name must be greater than 1 character.', category='error')
            elif password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif len(password1) < 7:
                flash('Password must be at least 7 characters.', category='error')
            else:
                #Add Salt
                salt = secrets.token_hex(32)
                password1 += salt     
                hash = generate_password_hash(password1, method='sha256') + salt
                new_user = User(username=username, email=email, name=name, password=hash)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created!', category='success')
                return redirect(url_for('views.home'))

    except Exception as e:
        return render_template("error.html", user=current_user)

    return render_template("signUp.html", user=current_user)

