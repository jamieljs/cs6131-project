from flask import flash, url_for, session, redirect, render_template, request
from forms import RecipeQueryForm
import tools
from math import ceil

def browse():
    userinfo = tools.getCurrentUserInfo()
    form = RecipeQueryForm()

    recipe_list = tools.getSavedRecipeQueryData()
    if recipe_list == None: # first time
        recipe_list = tools.newRecipeSearchQuery(None)

    # searching by creator/bookmark from profile page
    creator = request.args.get('creator')
    bookmarked = request.args.get('bookmarked')
    if creator != None and bookmarked != None:
        try:
            creator = int(creator)
            bookmarked = int(bookmarked)
            if bookmarked != 1 and bookmarked != 0:
                raise Exception
            recipe_list = tools.newRecipeSearchQuery({'search_creator_id':creator, 'search_bookmarked':bookmarked})
        except:
            flash('Invalid query parameters. Try querying via the user interface instead.', 'danger')
    elif creator != None:
        try:
            creator = int(creator)
            recipe_list = tools.newRecipeSearchQuery({'search_creator_id':creator})
        except:
            flash('Invalid query parameters. Try querying via the user interface instead.', 'danger')
    elif bookmarked != None:
        try:
            bookmarked = int(bookmarked)
            if bookmarked != 1 and bookmarked != 0:
                raise Exception
            recipe_list = tools.newRecipeSearchQuery({'search_bookmarked':bookmarked})
        except:
            flash('Invalid query parameters. Try querying via the user interface instead.', 'danger')

    # page number
    page = request.args.get('page')
    try:
        if page == None or page == "":
            page = 1
        page = int(page)
    except:
        return redirect('/browse?page=1')

    num_recipes = len(recipe_list)
    recipe_per_page = tools.recipe_per_page
    max_page_num = max(ceil(num_recipes / recipe_per_page), 1)

    if page < 1 or page > max_page_num:
        return redirect('/browse?page=1')

    pages_to_display = range(max(1, page - 1), min(max_page_num, page + 2) + 1)

    recipe_list = recipe_list[(page - 1) * recipe_per_page : min(num_recipes, page * recipe_per_page)]

    if form.validate_on_submit():
        result = request.form
        creator_info = tools.getUserInfoFromUsername(result['search_creator'])

        if creator_info == None:
            result['search_creator_id'] = -1
        else:
            result['search_creator_id'] = creator_info.user_id
        
        if result['search_bookmarked']:
            result['search_bookmarked'] = 1
        else:
            result['search_bookmarked'] = 0
        
        recipe_list = tools.newRecipeSearchQuery(result)
        num_recipes = len(recipe_list)
        max_page_num = max(ceil(num_recipes / recipe_per_page), 1)

        page = 1
        pages_to_display = range(1, min(max_page_num, 3) + 1)

    creator_usernames = tools.getUserNames()
    ingredient_names = tools.getIngredientNames()

    return render_template('browse.html', userinfo=userinfo, currentPage='recipe', form=form, linkname='/browse?', pageNum=page, maxPage=max_page_num, pages_to_display=pages_to_display, recipe_list=recipe_list, creator_usernames=creator_usernames, ingredient_names=ingredient_names)
