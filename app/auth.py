from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignUpForm, SignInForm

auth = Blueprint('auth', __name__)


@auth.route('/signin', methods=['POST', 'GET'])
def signin():
    form = SignInForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('views.index'))
            else:
                flash('Incorrect password!', category='danger')
        else:
            flash('Username does not exist!', category='danger')

    if current_user.is_authenticated:
        return redirect(url_for('views.index'))

    return render_template('signin.html', title="Sign In", form=form)


@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        firstName = form.first_name.data
        lastName = form.last_name.data
        name = f'{firstName.capitalize()} {lastName.capitalize()}'

        user = User.query.filter_by(username=username).first()

        if user:
            flash('Username already exists', category='danger')
        else:
            new_user = User(username=username, password=generate_password_hash(
                password, method="sha256"), name=name)

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for('views.index'))

    if current_user.is_authenticated:
        return redirect(url_for('views.index'))

    return render_template('signup.html', title="Sign Up", form=form)


@auth.route('/signout')
@login_required
def signout():
    logout_user()
    return redirect(url_for('auth.signin'))
