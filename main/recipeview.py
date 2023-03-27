from flask import flash, url_for, session, redirect, render_template, request
from forms import DeleteRecipeForm
import tools

def recipe(recipe_id):
    if 'loggedin' in session:
        userid = session['id']
    else:
        userid = None
    recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
    if recipeinfo == None:
        flash('Page could not be found!', 'warning')
        return redirect('/') 

    recipe_ratings=tools.getRecipeRatings(recipe_id)
    num_reviews = 0
    for i in range(5):
        num_reviews += recipe_ratings[i]
    form = DeleteRecipeForm()

    result = request.form
    if 'form_name' in result and result['form_name'] == 'toggle-follow':
        tools.toggleFollow(userid, recipeinfo['creator_id'])
    elif 'form_name' in result and result['form_name'] == 'toggle-bookmark':
        tools.toggleBookmark(userid, recipeinfo['recipe_id'])
        recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
    elif 'form_name' in result and result['form_name'] == 'rating':
        if 'ratings' in result:
            rating = result['ratings']
            tools.updateRating(userid, recipeinfo['recipe_id'], rating)
            flash('Rating added', 'success')
        else:
            tools.updateRating(userid, recipeinfo['recipe_id'], None)
            flash('Rating removed!', 'success')
        recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
    elif form.is_submitted():
        if form.delete_recipe.data and form.validate():
            tools.deleteRecipe(recipeinfo['recipe_id'])
            return redirect('/browse?creator=' + userid)
        else:
            flash('Recipe deletion failed. Please try again.', 'danger')

    return render_template('recipe.html', user_is_following_creator=tools.isFollowingProfile(recipeinfo['creator_id']), user_bookmarked_recipe=tools.bookmarkedRecipe(recipeinfo['recipe_id']), recipeinfo=recipeinfo, form=form, recipe_ratings=recipe_ratings, num_reviews=num_reviews)