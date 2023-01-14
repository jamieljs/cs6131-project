from flask import flash, url_for, session, redirect, render_template, request
from forms import EditRecipeForm
import tools

def editrecipe(recipe_id):
    userinfo = tools.getCurrentUserInfo()
    recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)

    if userinfo == None or userinfo['user_id'] != recipeinfo['recipe_creator']:
        flash('You do not have access this page!', 'warning')
        return redirect('/')
    
    form = EditRecipeForm()

    if form.validate_on_submit():
        pass

    return render_template('editrecipe.html', userinfo=userinfo, recipeinfo=recipeinfo, currentPage='recipe', form=form)
