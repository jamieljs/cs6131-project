from flask import flash, url_for, session, redirect, render_template, request
import tools
import datetime
from forms import AddInventoryForm

def inventory():
    userinfo = tools.getCurrentUserInfo()
    if userinfo == None:
        flash('You do not have access this page!', 'warning')
        redirect('/')
    
    inventory = tools.getInventoryOfUser(userinfo['user_id'])
    ingredient_names = tools.getIngredientNames()

    form = AddInventoryForm()

    result = request.form
    if 'form_name' in result and result['form_name'] == 'delete-ingredient':
        tools.removeIngredientFromInventory(userinfo['user_id'], result['delete_ingredient_id'], result['delete_expiry_date'])
    elif form.is_submitted():
        if form.submit_add_inventory.data and form.validate():
            ingredient_id = tools.getIngredientIdFromIngredientName(result['inventory_ingredient'])
            if ingredient_id != None:
                tools.addIngredientToInventory(userinfo['user_id'], ingredient_id, result['expiry_date'])
            else:
                flash('Addition of ingredient to inventory failed. Please choose an ingredient from the autocomplete list and try again.', 'danger')
        else:
            flash('Addition of ingredient to inventory failed. Please try again.', 'danger')
    
    return render_template('inventory.html', userinfo=userinfo, inventory=inventory, currentPage='inventory', form=form, today_date=datetime.datetime.now().date(), ingredient_names=ingredient_names)
