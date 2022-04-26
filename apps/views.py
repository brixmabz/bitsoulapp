from functools import reduce
from flask import Blueprint, flash, render_template, redirect, request, url_for, jsonify, session
from flask_login import login_required, current_user
from .models import Task, Note, User
from . import db
import json
from werkzeug.security import check_password_hash, generate_password_hash
from .forms import UpdateNameForm, UpdatePasswordForm

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
