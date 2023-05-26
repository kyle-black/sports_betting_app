from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from .models import User

class UniqueUsername:
    def __init__(self, message="Username already exists."):
        self.message = message

    def __call__(self, form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError(self.message)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')    
    submit = SubmitField('Log In')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign Up')