import flask
from flask import Flask,session,flash,redirect,url_for,render_template,abort

from main import browseview, editrecipeview, feedbackview, homeview, inventoryview, loginview, profileview, recipeview

import tools
from extensions import mysql

app = Flask(__name__)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'cs6131proj'
mysql.init_app(app)

app.add_url_rule('/', view_func = homeview.home)

app.add_url_rule('/browse', view_func = browseview.browse, methods=['GET', 'POST'])
app.add_url_rule('/editrecipe/<int:recipe_id>', view_func = editrecipeview.editrecipe, methods=['GET', 'POST'])
app.add_url_rule('/feedback', view_func = feedbackview.feedback, methods=['GET', 'POST'])
app.add_url_rule('/inventory', view_func = inventoryview.inventory, methods=['GET', 'POST'])
app.add_url_rule('/login', view_func = loginview.login, methods=['GET', 'POST'])
app.add_url_rule('/profile/<int:user_id>', view_func = profileview.profile, methods=['GET', 'POST'])
app.add_url_rule('/recipe/<int:recipe_id>', view_func = recipeview.recipe, methods=['GET', 'POST'])

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful!', 'info')
    return redirect('/')

@app.route('/createrecipe')
def createRecipe():
    if 'loggedin' in session:
        recipe_id = tools.newRecipe(session['id'])
        return redirect('/editrecipe/' + str(recipe_id))
    else:
        flash('Cannot create a recipe without being logged in!', 'danger')
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)

    