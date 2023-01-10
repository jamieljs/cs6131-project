from flask import flash, render_template, request, redirect, url_for
from forms import QueryForm
import tools
from math import ceil

def browserecipe():
    userinfo = tools.getCurrentUserInfo()
    form = QueryForm()

    page = request.args.get('page')
    try:
        if page is None or page == "":
            page = 1
        page = int(page)
    except:
        redirect('/browse?page=1')

    recipe_list = tools.getSavedQueryData()
    num_recipes = len(recipe_list)
    recipe_per_page = tools.recipe_per_page
    max_page_num = ceil(num_recipes / recipe_per_page)
    
    pages_to_display = range(max(1, page - 1), min(max_page_num, page + 2) + 1)

    recipe_list = recipe_list[(page - 1) * recipe_per_page : min(num_recipes, page * recipe_per_page)]

    if form.validate_on_submit():
        recipe_list = tools.newSearchQuery(request.form)
        num_recipes = len(recipe_list)
        max_page_num = ceil(num_recipes / recipe_per_page)

        page = 1
        pages_to_display = range(1, min(max_page_num, 3) + 1)

    return render_template('browserecipe.html', userinfo=userinfo, currentPage='recipe', form=form, page=page, pages_to_display=pages_to_display)
