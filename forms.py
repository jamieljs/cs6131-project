from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, TextAreaField, validators
from wtforms.validators import InputRequired, Email, EqualTo, Length
import tools

class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired("Please enter your username.")], render_kw={"placeholder": "username"})
    password = PasswordField('Password', [InputRequired("Please enter your password.")], render_kw={"placeholder": "password"})
    login = SubmitField('Login')

class RegisterForm(FlaskForm):
    reg_username = StringField('Username', [InputRequired("Please enter a username."), Length(min=3)], render_kw={"placeholder": "username"})
    reg_email = StringField('Email', [InputRequired("Please enter your email."), Email("This field requires a valid email address.")], render_kw={"placeholder": "email@example.com"})
    reg_password = PasswordField('Password', [InputRequired("Please enter a password."), Length(min=6, max=30), EqualTo("confirm_password", message="Passwords must match")], render_kw={"placeholder": "password"})
    confirm_password = PasswordField('Confirm Password', [InputRequired("Please confirm your password."), EqualTo("reg_password", message="Passwords must match")], render_kw={"placeholder": "confirm_password"})
    register = SubmitField('Register')

class FeedbackForm(FlaskForm):
    feedback_text = TextAreaField('Feedback', [InputRequired("Cannot submit empty feedback!"), Length(min=10)], render_kw={"placeholder": "feedback", "style": "height: 400px;"})
    submit_feedback = SubmitField('Submit Feedback')

class QueryForm(FlaskForm):
    search_text = StringField(None) # name or description
    search_cuisine = StringField('Cuisine') # cuisine contains string as substring
    search_my_ingredients = BooleanField("Filter by my ingredients") # contains only ingredients that the user has; only if signed in
    search_show_private = BooleanField("Show private recipes") # show private recipes; only if signed in
    search_tags = [] # recipes shown must contain all chosen tags
    for tag in tools.recipe_tags:
        search_tags.append(BooleanField(tag))
    sort_rating = SelectField("Rating:", validators=[InputRequired()], choices=[('no', 'Do not sort by rating'), ('good', 'Sort from highest to lowest rating'), ('bad', 'Sort from lowest to highest rating')], default='no')
    submit_search = SubmitField("Filter Recipes")
