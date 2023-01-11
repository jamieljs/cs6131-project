from flask import flash, render_template, request, redirect, url_for
from forms import RecipeQueryForm
import tools
from math import ceil

def browserecipe():
    userinfo = tools.getCurrentUserInfo()
    form = RecipeQueryForm()

    recipe_list = tools.getSavedRecipeQueryData()
    if recipe_list == None: # first time
        recipe_list = tools.newRecipeSearchQuery(None)

    # searching by creator from profile page
    creator = request.args.get('creator')
    if creator != None:
        try:
            creator = int(creator)
            recipe_list = tools.newRecipeSearchQuery({'search_creator_id':creator})
        except:
            recipe_list = tools.newRecipeSearchQuery({'search_creator_id':-1})

    # page number
    page = request.args.get('page')
    try:
        if page is None or page == "":
            page = 1
        page = int(page)
    except:
        redirect('/browserecipe?page=1')

    num_recipes = len(recipe_list)
    recipe_per_page = tools.recipe_per_page
    max_page_num = max(ceil(num_recipes / recipe_per_page), 1)

    if page < 1 or page > max_page_num:
        redirect('/browserecipe?page=1')

    pages_to_display = range(max(1, page - 1), min(max_page_num, page + 2) + 1)

    recipe_list = recipe_list[(page - 1) * recipe_per_page : min(num_recipes, page * recipe_per_page)]

    if form.validate_on_submit():
        result = request.form
        creator_info = tools.getUserInfoFromUsername(result['search_creator'])
        if creator_info == None:
            result['search_creator_id'] = -1
        else:
            result['search_creator_id'] = creator_info.user_id
        
        recipe_list = tools.newRecipeSearchQuery(result)
        num_recipes = len(recipe_list)
        max_page_num = max(ceil(num_recipes / recipe_per_page), 1)

        page = 1
        pages_to_display = range(1, min(max_page_num, 3) + 1)

    print(recipe_list)

    return render_template('browserecipe.html', userinfo=userinfo, currentPage='recipe', form=form, linkname='/browserecipe?', pageNum=page, maxPage=max_page_num, pages_to_display=pages_to_display, recipe_list=recipe_list)
