from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import re


auth = Blueprint('auth', __name__)

regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
regex_username = re.compile(r'^[a-zA-Z0-9_.-]+$')
regex_password = re.compile(r'[A-Za-z0-9@#$]{6,12}')

def isValidEmail(email):
    if re.fullmatch(regex_email, email):
        return True
    else:
        return False


def isValidUsername(username):
    if re.fullmatch(regex_username, str(username)):
        return True
    else:
        return False


def isValidPassword(password):
    if re.fullmatch(regex_password, password):
        return True
    else:
        return False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Login Successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('There\'s no account with this email, try again.', category='error')
    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        user_temp2 =  User.query.filter_by(username=username).first()
        if user:
            flash('There is an account with this email. Please try another email.', category='error')
        elif not isValidEmail(email):
            flash('Invalid email! Please try again.', category='error')
        elif not isValidUsername(username):
            flash('Invalid username! Please try again.', category='error')
        elif not isValidPassword(password1):
            flash('Invalid password! Please try again.', category='error')
        elif password1 != password2:
            flash('The passwords don\'t match.', category='error')
        elif user_temp2:
            flash('Username has been existed, try again with another username.', category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)
