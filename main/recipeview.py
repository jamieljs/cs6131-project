from flask import flash, url_for, session, redirect, render_template, request
from forms import DeleteRecipeForm
import tools

def recipe(recipe_id):
    userinfo = tools.getCurrentUserInfo()
    recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
    form = DeleteRecipeForm()

    if form.validate_on_submit():
        tools.deleteRecipe(recipeinfo.recipe_id)
        redirect('/browse?creator=' + userinfo.user_id)

    return render_template('recipe.html', userinfo=userinfo, recipeinfo=recipeinfo, form=form, currentPage='recipe')