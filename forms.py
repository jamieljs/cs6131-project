from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField, validators, widgets
from wtforms.validators import InputRequired, Email, EqualTo, Length, ValidationError
import tools

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(html_tag="ul", prefix_label=False)
    option_widget = widgets.CheckboxInput()

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

class RecipeQueryForm(FlaskForm):
    search_text = StringField(None, render_kw={"placeholder": "Search by recipe name or description..."}) # name or description
    search_creator = StringField(None, render_kw={"placeholder": "Enter username of creator"}) # username
    search_cuisine = MultiCheckboxField(None, choices=tools.cuisine_tags) # recipes shown can contain any chosen tag
    search_my_ingredients = BooleanField("Filter by my ingredients") # contains only ingredients that the user has; only if signed in
    search_show_private = BooleanField("Show private recipes") # show private recipes; only if signed in
    search_tags = MultiCheckboxField(None, choices=tools.recipe_tags) # recipes shown must contain all chosen tags

    sort_attribute = SelectField("Sort by:", validators=[InputRequired()], choices=[('difficulty', 'Difficulty'), ('cooktime', 'Preparation and Cooking Duration'), ('rating', 'Rating')], default='no')
    sort_direction = SelectField("Order:", validators=[InputRequired()], choices=['None', 'Increasing', 'Decreasing'], default='None')

    submit_search = SubmitField("Filter Recipes")

class CollectionQueryForm(FlaskForm):
    submit_search = SubmitField("Filter Collections")

class DeleteRecipeForm(FlaskForm):
    delete_recipe = SubmitField("Delete Recipe")

class DeleteCollectionForm(FlaskForm):
    delete_collection = SubmitField("Delete Collection")

class EditProfileForm(FlaskForm):
    profile_username = StringField('Username', [InputRequired(), Length(min=3)])
    profile_description = TextAreaField('Description')
    profile_email = StringField('Email', [InputRequired(), Email("This field requires a valid email address.")])
    profile_submit = SubmitField('Save Changes')
