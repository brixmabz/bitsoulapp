from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=6, max=40, message=None)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=40, message=None)])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    submit = SubmitField('Submit')


class SignInForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Submit')

class UpdateNameForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    submit = SubmitField('Submit')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[InputRequired()])
    new_password1 = PasswordField('New Password', validators=[InputRequired()])
    new_password2 = PasswordField('Confirm New Password', validators=[InputRequired()])
    submit = SubmitField('Submit')