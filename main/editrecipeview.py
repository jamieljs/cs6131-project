from flask import flash, url_for, session, redirect, render_template, request
import tools

def editrecipe(recipe_id):
    userinfo = tools.getCurrentUserInfo()
    recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
    if recipeinfo == None:
        flash('Page could not be found!', 'warning')
        return redirect('/')
    if userinfo == None or userinfo['user_id'] != recipeinfo['recipe_creator']:
        flash('You do not have access this page!', 'warning')
        return redirect('/')

    ingredient_names = tools.getIngredientNames()

    result = request.form

    # TODO
    if 'form_name' in result:
        if result['form_name'] == 'name':
            pass
        elif result['form_name'] == 'description':
            pass
        elif result['form_name'] == 'image':
            pass
        elif result['form_name'] == 'add-ingredient':
            # throw error if exists
            pass
        elif result['form_name'] == 'delete-ingredient':
            pass
        elif result['form_name'] == 'add-instruction':
            pass
        elif result['form_name'] == 'update-instruction-list':
            pass
        elif result['form_name'] == 'portions':
            pass
        elif result['form_name'] == 'cook-time':
            pass
        elif result['form_name'] == 'difficulty':
            pass
        elif result['form_name'] == 'cuisine':
            pass
        elif result['form_name'] == 'dietary':
            pass
        elif result['form_name'] == 'tag':
            pass
        else:
            flash('Recipe editing failed. Please try again.', 'danger')
    
    return render_template('editrecipe.html', userinfo=userinfo, recipeinfo=recipeinfo, currentPage='recipe', ingredient_names=ingredient_names)
