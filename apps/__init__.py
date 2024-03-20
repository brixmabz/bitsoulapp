from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from os import path
from flask_login import LoginManager
from apps import app_config
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    Session(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    db.init_app(app)

    from .views import views
    from .auth import auth, _build_auth_code_flow

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Task, Note

    create_db(app)

    app.jinja_env.globals.update(
        _build_auth_code_flow=_build_auth_code_flow)  # Used in template

    login_manager = LoginManager()
    login_manager.login_view = 'auth.signin'
    login_manager.login_message = ''
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_db(app):
    if not path.exists('instance/' + DB_NAME):
        with app.app_context():
            db.create_all()
