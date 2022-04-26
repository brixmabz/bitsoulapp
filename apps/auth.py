from cmath import log
from hashlib import new
from unicodedata import name
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import requests
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignUpForm, SignInForm
import msal
from apps import app_config

auth = Blueprint('auth', __name__)


@auth.route('/signin', methods=['POST', 'GET'])
def signin():
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)

    return redirect(session["flow"]["auth_uri"])


@auth.route('/authdata')
def auth_data():
    if session.get("user"):
        user = User.query.filter_by(
            email=session["user"]["preferred_username"]).first()

        if not user:
            new_user = User(
                email=session["user"]["preferred_username"], name=session["user"]["name"])

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
        else:
            login_user(user)

    return redirect(url_for("views.index"))


@auth.route(app_config.REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("auth.auth_data"))


@auth.route("/signout")
def logout():
    logout_user()
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("views.index", _external=True))


@auth.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("auth.signin"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    return render_template('display.html', result=graph_data)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("auth.authorized", _external=True))


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result
