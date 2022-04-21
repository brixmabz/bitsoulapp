from functools import reduce
from flask import Blueprint, flash, render_template, redirect, request, url_for, jsonify
from flask_login import login_required, current_user
from .models import Task, Note, User
from . import db
import json
from werkzeug.security import check_password_hash, generate_password_hash

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def index():
    return render_template('index.html', title="Home", user=current_user)


@views.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        task = request.form.get('taskData')
        new_task = Task(task=task, user_id=current_user.id)

        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('views.tasks'))

    return render_template('tasks.html', title='Task Manager', tasks=tasks, user=current_user)


@views.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    notes = Note.query.filter_by(user_id=current_user.id).all()

    if request.method == 'POST':
        note = request.form.get('noteData')
        new_note = Note(note=note, user_id=current_user.id)

        db.session.add(new_note)
        db.session.commit()

        return redirect(url_for('views.notes'))

    return render_template('notes.html', title='Notes Manager', notes=notes, user=current_user)


@views.route('/notes/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)

    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return redirect(url_for('views.notes'))


@views.route('/tasks/delete', methods=['GET', 'POST'])
@login_required
def delete_task():
    data = json.loads(request.data)
    task_id = data['id']

    task = Task.query.get_or_404(task_id)

    if task:
        if task.user_id == current_user.id:
            db.session.delete(task)
            db.session.commit()

    return jsonify({})


@views.route('/tasks/update', methods=['GET', 'POST'])
@login_required
def update_task():
    data = json.loads(request.data)

    task = Task.query.get_or_404(data['id'])

    if task:
        if task.user_id == current_user.id:
            task.task = data['task']
            db.session.commit()

    return jsonify({})


@views.route('/tasks/get', methods=['GET', 'POST'])
@login_required
def get_task():
    if request.method == "POST":
        data = json.loads(request.data)
        task_id = data['id']

        task = Task.query.get_or_404(task_id)

        if task:
            if task.user_id == current_user.id:
                task_data = {
                    'task': task.task,
                    'id': task.id
                }
                print(task_data)
                return jsonify(task_data)

    return jsonify({})


@views.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account.html', title='Account', user=current_user)


@views.route('/update/user/<option>', methods=['GET', 'POST'])
@login_required
def update_user(option):
    if request.method == 'POST':
        if option == "name":
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')

            if len(first_name) < 3:
                flash("First name too short!", category='danger')
            elif len(last_name) < 3:
                flash("Last name too short!", category='danger')
            else:
                name = f'{first_name} {last_name}'

                user = User.query.get_or_404(current_user.id)
                user.name = name
                db.session.commit()
                flash('Name changed!', category="success")

        elif option == "password":
            old_password = request.form.get('oldPassword')
            new_password1 = request.form.get('password1')
            new_password2 = request.form.get('password2')

            user = User.query.get_or_404(current_user.id)

            if check_password_hash(user.password, old_password):
                if new_password1 == new_password2:
                    user.password = generate_password_hash(
                        new_password1, method="sha256")
                    db.session.commit()
                    flash('Password changed!', category="success")
                else:
                    flash("New passwords don't match!", category='danger')
            else:
                flash('Incorrect old password!', category='danger')

    return redirect(url_for('views.account'))
