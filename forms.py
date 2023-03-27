from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, DecimalField, PasswordField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField, validators, widgets
from wtforms.validators import InputRequired, EqualTo, Length, ValidationError
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
    reg_username = StringField('Username', [InputRequired("Please enter a username."), Length(min=3, max=15)], render_kw={"placeholder": "username"})
    reg_password = PasswordField('Password', [InputRequired("Please enter a password."), Length(min=6, max=30), EqualTo("confirm_password", message="Passwords must match")], render_kw={"placeholder": "password"})
    confirm_password = PasswordField('Confirm Password', [InputRequired("Please confirm your password."), EqualTo("reg_password", message="Passwords must match")], render_kw={"placeholder": "confirm_password"})
    register = SubmitField('Register')

class FeedbackForm(FlaskForm):
    feedback_text = TextAreaField('Feedback', [InputRequired("Cannot submit empty feedback!"), Length(min=10)], render_kw={"placeholder": "feedback", "style": "height: 400px;"})
    submit_feedback = SubmitField('Submit Feedback')

class RecipeQueryForm(FlaskForm):
    search_text = StringField(None, render_kw={"placeholder": "Search by recipe name or description..."}) # name or description
    search_creator = StringField(None, render_kw={"placeholder": "Enter username of creator"}) # username
    search_ingredient = StringField(None, render_kw={"placeholder": "Enter name of ingredient to include"}) # ingredient
    search_cuisine = MultiCheckboxField(None) # recipes shown can contain any chosen tag
    search_dietary = MultiCheckboxField(None) # recipes shown must contain all chosen tags
    search_my_ingredients = BooleanField("Filter by my ingredients") # contains only ingredients that the user has; only if signed in
    search_bookmarked = BooleanField("Show only bookmarked recipes")

    sort_attribute = SelectField("Sort by:", validators=[InputRequired()], choices=[('date', 'Date Created'), ('difficulty', 'Difficulty'), ('duration', 'Preparation and Cooking Duration'), ('rating', 'Rating')], default='date')
    sort_direction = SelectField("Order:", validators=[InputRequired()], choices=[('DESC', 'Decreasing'), ('ASC', 'Increasing')], default='DESC')

    submit_search = SubmitField("Filter Recipes")

class DeleteRecipeForm(FlaskForm):
    delete_recipe = SubmitField("Delete Recipe")

class EditProfileForm(FlaskForm):
    profile_username = StringField('Username', [InputRequired(), Length(min=3)])
    profile_description = TextAreaField('Description')
    profile_submit = SubmitField('Save Changes')

class AddInventoryForm(FlaskForm):
    inventory_ingredient = StringField('Search Ingredient Name (Autocomplete):', [InputRequired()])
    expiry_date = DateField('Select Expiry Date:', [InputRequired()])
    submit_add_inventory = SubmitField('Add Ingredient to Inventory')
