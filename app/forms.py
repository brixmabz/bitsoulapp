from flask_wtf import Form
from wtforms import StringField, SubmitField


class SignUpForm(Form):
    username = StringField('Username')
    submit = SubmitField('Submit')
