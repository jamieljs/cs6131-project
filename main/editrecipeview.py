from flask import flash, url_for, session, redirect, render_template, request
import tools, forms, math

def editname():
    target_id = request.form['target_id']
    if target_id:
        tools.editRecipeName(target_id, request.form['name'])
        return {'status':200,'error':''}
    return {'status':300,'error':'Access to resource denied'}

def editdesc():
    target_id = request.form['target_id']
    if target_id:
        tools.editRecipeDescription(target_id, request.form['desc'])
        return {'status':200,'error':''}
    return {'status':300,'error':'Access to resource denied'}

def editimage():
    target_id = request.form['target_id']
    if target_id:
        tools.editRecipeImage(target_id, request.form['image'])
        return {'status':200,'error':''}
    return {'status':300,'error':'Access to resource denied'}

def editportions():
    target_id = request.form['target_id']
    portions = request.form['portions']
    if target_id:
        tools.editRecipePortions(target_id, portions)
        return {'status':200,'error':''}
    return {'status':300,'error':'Access to resource denied'}

def editduration():
    target_id = request.form['target_id']
    duration = request.form['duration']
    if target_id:
        tools.editRecipeDuration(target_id, duration)
        return {'status':200,'error':''}
    return {'status':300,'error':'Access to resource denied'}

def editdifficulty():
    target_id = request.form['target_id']
    if target_id:
        tools.editRecipeDifficulty(target_id, request.form['difficulty'])
        return {'status':200,'error':''}
    return {'status':300,'error':'Access to resource denied'}

def editinstructions():
    pass

def editcuisines():
    target_id = request.form['target_id']
    if target_id:
        tools.editRecipeCuisineTags(target_id, request.form['cuisines'])
        return {'status':200,'error':''}
    return {'status':300,'error':'Access to resource denied'}

def editrecipe(recipe_id):
    recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
    if recipeinfo == None:
        flash('Recipe could not be found!', 'warning')
        return redirect('/')
    if 'loggedin' not in session or session['id'] != recipeinfo['creator_id']:
        flash('You do not have access to this page!', 'warning')
        return redirect('/')

    userid = session['id']
    ingredient_names = tools.getIngredientNames()
    cuisine_form = forms.EditRecipeCuisinesForm()
    cuisine_form.options.choices =  tools.getCuisineTags()

    cur_cuisine_ids = []
    for cuisine in recipeinfo['cuisines']:
        cur_cuisine_ids.append(cuisine['cuisine_id'])

    result = request.form

    if cuisine_form.edit_cuisines.data and cuisine_form.is_submitted():
        old_cuisine_ids = []
        for cuisine in recipeinfo['cuisines']:
            old_cuisine_ids.append(cuisine['cuisine_id'])
        selection = result.getlist('options')
        difference = []
        cuisine_tags = tools.getCuisineTags()

        current_cuisines = []
        for cuisine in cuisine_tags:
            if cuisine[0] in selection and cuisine[0] not in old_cuisine_ids:
                difference.append((cuisine[0], 1))
            elif cuisine[0] not in selection and cuisine[0] in old_cuisine_ids:
                difference.append((cuisine[0], -1))
            if cuisine[0] in selection:
                current_cuisines.append(cuisine)
        
        tools.editRecipeCuisineTags(recipe_id, difference)
        recipeinfo['cuisines'] = current_cuisines
        cur_cuisine_ids = selection

    elif request.method == 'POST' and 'form_name' in result:
        if result['form_name'] == 'delete-ingredient':
            tools.deleteRecipeIngredient(recipe_id, result['delete_ingredient_id'])
            recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
        elif result['form_name'] == 'add-ingredient':
            ingredient_id = tools.getIngredientIdFromIngredientName(result['ingredient_input'])
            if ingredient_id != None:
                tools.addRecipeIngredient(recipe_id, ingredient_id, result['quantity'])
                recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
            else:
                flash('Addition of ingredient to recipe failed. Please choose an ingredient from the autocomplete list and try again.', 'danger')
        elif result['form_name'] == 'add-instruction':
            tools.addRecipeInstruction(recipe_id, result['instruction_title'], result['instruction_subtitle'])
            recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
        elif result['form_name'] == 'delete-instruction':
            tools.deleteRecipeInstruction(recipe_id, result['instruction_id'])
            recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
        elif result['form_name'] == 'up-instruction':
            tools.upRecipeInstruction(recipe_id, result['instruction_id'])
            recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)
        elif result['form_name'] == 'down-instruction':
            tools.downRecipeInstruction(recipe_id, result['instruction_id'])
            recipeinfo = tools.getRecipeInfoFromRecipeId(recipe_id)

    return render_template('editrecipe.html', recipeinfo=recipeinfo, ingredient_names=ingredient_names, cur_cuisine_ids=cur_cuisine_ids, cuisine_form=cuisine_form)
