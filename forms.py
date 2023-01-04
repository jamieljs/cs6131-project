from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, BooleanField, PasswordField, SelectField, SubmitField, TextAreaField, validators
from wtforms.validators import InputRequired, Email, EqualTo

class LoginForm(FlaskForm):
    username = StringField('username', [InputRequired("Please enter your username.")])
    password = PasswordField('password', [InputRequired("Please enter your password.")])
    login = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('username', [InputRequired("Please enter a username.")])
    email = StringField('email', [InputRequired("Please enter your email."), Email("This field requires a valid email address.")])
    password = PasswordField('password', [InputRequired("Please enter a password.")])
    confirm_password = PasswordField('confirm_password', [InputRequired("Please confirm your password."), EqualTo("password", message="Passwords must match")])
    register = SubmitField('Register')


