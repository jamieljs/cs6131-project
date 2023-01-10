import flask
from flask import Flask,Blueprint,session,flash,redirect,url_for,render_template,abort, send_from_directory

from main import browserecipeview, editprofileview, editrecipeview, feedbackview, homeview, inventoryview, loginview, profileview, recipeview

app = Flask(__name__)

import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


app.add_url_rule('/browse', view_func = browserecipeview.browse)
app.add_url_rule('/editprofile', view_func = editprofileview.editprofile)
app.add_url_rule('/editrecipe/<int:recipe_id>', view_func = editrecipeview.editrecipe)
app.add_url_rule('/feedback', view_func = feedbackview.feedback, methods=['GET', 'POST'])
app.add_url_rule('/inventory', view_func = inventoryview.inventory, methods=['GET', 'POST'])
app.add_url_rule('/login', view_func = loginview.login, methods=['GET', 'POST'])
app.add_url_rule('/profile/<int:user_id>', view_func = profileview.profile)
app.add_url_rule('/recipe/<int:recipe_id>', view_func = recipeview.recipe)
app.add_url_rule('/', view_func = homeview.home)

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    flash('Logout successful!', 'info')
    return redirect('/')

if __name__ == '__main__':

    app.run(debug=True)

    '''
    if len(sys.argv) <= 1 or sys.argv[1] != "develop":
        print("DEPLOY MODE")
        serve(app, host='0.0.0.0', port=5000, url_scheme='https', threads = 16)
    else:
        print("DEVELOP MODE")
        app.run(debug=True, host='0.0.0.0', port=443)
    '''
