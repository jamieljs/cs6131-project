from flask import flash, url_for, session, redirect, render_template, request
from forms import RecipeQueryForm
import tools
from math import ceil

def browse():
    form = RecipeQueryForm()

    form.search_cuisine.choices = tools.getCuisineTags()
    form.search_dietary.choices = tools.getDietaryTags()

    recipe_per_page = tools.recipe_per_page

    page = request.args.get('page')
    try:
        if page == None or page == "":
            page = 1
        page = int(page)
    except:
        return redirect('/browse?page=1')

    result = request.form
    query = dict({'text': '', 'creator_id': 0, 'ingredient': '', 'cuisine': [], 'dietary': [], 'my_ingredients': False, 'bookmarked': False, 'sort_attribute': 'date', 'sort_direction': 'DESC'})
    if request.method == 'POST': # new search query
        if 'profile_someones_recipes' in result:
            query['creator_id'] = result['profile_creator_id']
        elif 'profile_my_recipes' in result:
            query['creator_id'] = session['id']
        elif 'profile_bookmarked' in result:
            query['bookmarked'] = True
        elif form.validate_on_submit():
            if result['search_text']:
                query['text'] = result['search_text']
            query['creator_id'] = tools.getUserIdFromUsername(result['search_creator'])
            if result['search_ingredient']:
                query['ingredient'] = result['search_ingredient']
            if result.getlist('search_cuisine'):
                query['cuisine'] = result.getlist('search_cuisine')
            if result.getlist('search_dietary'):
                query['dietary'] = result.getlist('search_dietary')
            if 'my_ingredients' in result and result['my_ingredients']:
                query['my_ingredients'] = result['my_ingredients']
            if 'search_bookmarked' in result and result['search_bookmarked']:
                query['bookmarked'] = result['search_bookmarked']
            if result['sort_attribute']:
                query['sort_attribute'] = result['sort_attribute']
            if result['sort_direction']:
                query['sort_direction'] = result['sort_direction']

        recipe_list = tools.newRecipeSearchQuery(query)
        page = 1
    else:
        recipe_list = tools.getSavedRecipeQueryData()
        if recipe_list == None: # first time
            recipe_list = tools.newRecipeSearchQuery(query) # default

    num_recipes = len(recipe_list)
    max_page_num = max(ceil(num_recipes / recipe_per_page), 1)
    if page < 1 or page > max_page_num:
        return redirect('/browse?page=1')
    pages_to_display = range(max(1, page - 1), min(max_page_num, page + 2) + 1)

    recipe_list = recipe_list[(page - 1) * recipe_per_page : min(num_recipes, page * recipe_per_page)]
    creator_usernames = tools.getUserNames()
    ingredient_names = tools.getIngredientNames()

    return render_template('browse.html', form=form, linkname='/browse?', pageNum=page, maxPage=max_page_num, pages_to_display=pages_to_display, recipe_list=recipe_list, creator_usernames=creator_usernames, ingredient_names=ingredient_names)
