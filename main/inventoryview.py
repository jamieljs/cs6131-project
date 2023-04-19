from flask import flash, url_for, session, redirect, render_template, request
import tools
import datetime
from forms import AddInventoryForm

def inventory():
    if 'loggedin' not in session:
        flash('You do not have access to this page!', 'warning')
        return redirect('/')
    userid = session['id']

    inventory = tools.getInventoryOfUser(userid)
    ingredient_names = tools.getIngredientNames()

    form = AddInventoryForm()

    result = request.form
    if 'form_name' in result and result['form_name'] == 'delete-ingredient':
        tools.removeIngredientFromInventory(userid, result['delete_ingredient_id'], result['delete_expiry_date'])
        inventory = tools.getInventoryOfUser(userid)
    elif form.is_submitted():
        if form.submit_add_inventory.data and form.validate():
            ingredient_id = tools.getIngredientIdFromIngredientName(result['inventory_ingredient'])
            if ingredient_id != None:
                tools.addIngredientToInventory(userid, ingredient_id, result['expiry_date'])
                inventory = tools.getInventoryOfUser(userid)
            else:
                flash('Addition of ingredient to inventory failed. Please choose an ingredient from the autocomplete list and try again.', 'danger')
        else:
            flash('Addition of ingredient to inventory failed. Please try again.', 'danger')
    
    return render_template('inventory.html', inventory=inventory, form=form, today_date=datetime.datetime.now(), ingredient_names=ingredient_names)
