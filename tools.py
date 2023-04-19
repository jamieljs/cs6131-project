from flask import session, flash
import copy
import datetime
import re
from extensions import mysql
import MySQLdb.cursors
from werkzeug.security import check_password_hash, generate_password_hash

# LOGIN / USERS

def login(username, password):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
    account = cursor.fetchone()
    cursor.close()

    if account:
        if check_password_hash(account['password'], password):
            flash('Welcome, ' + str(username) + '!', 'success')
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
            return True
        else:
            flash('Password is incorrect. Please try again.', 'danger')
    else:
        flash('User does not exist. Please try again.', 'danger')
    
    return False

def register(username, password):
    if isValidUsername(username, 0):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, NULL)', (username, generate_password_hash(password),))
        cursor.close()
        mysql.connection.commit() #commit the insertion
        login(username, password)
        return True
    return False

def deleteAccount(user_id, password):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE user_id=%s', (user_id,))
    account = cursor.fetchone()
    if account:
        if check_password_hash(account['password'], password):
            cursor.execute('DELETE FROM user WHERE user_id=%s', (user_id,))
            cursor.close()
            mysql.connection.commit()
            flash('Your account was successfully deleted and you have been logged out', 'success')
            # redirect to logout from the other side
            return True
        else:
            cursor.close()
            flash('Password is incorrect. Account could not be deleted. Please try again.', 'danger')
    else:
        cursor.close()
        flash('Something went wrong. Please try again.', 'danger')
    return False

def getProfileInfoFromUserId(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
    account = cursor.fetchone()
    if account == None:
        return None
    cursor.execute('SELECT follower_id, username FROM follows, user WHERE following_id = %s and follower_id = user_id', (user_id,))
    account['followers'] = cursor.fetchall()
    cursor.execute('SELECT following_id, username FROM follows, user WHERE follower_id = %s and following_id = user_id', (user_id,))
    account['following'] = cursor.fetchall()
    cursor.execute('SELECT AVG(recipe_rating) as avg FROM recipe WHERE creator_id = %s', (user_id,))
    result = cursor.fetchone()
    if result:
        account['avg_rating'] = result['avg']
    else:
        account['avg_rating'] = None
    cursor.close()
    return account

def isValidUsername(username, user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
    account = cursor.fetchone()
    
    if account and account['user_id'] != user_id:
        flash('This username is taken. Please try again.', 'danger')
        return False
    elif not re.match(r'[A-Za-z0-9]+', username):
        flash('Username must only contain letters and numbers. Please try again.', 'danger')
        return False
    return True

def getUserIdFromUsername(username):
    if username == None:
        return 0
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT user_id FROM user WHERE username = %s', (username,))
    account = cursor.fetchone()
    cursor.close()
    if account == None:
        return 0
    return account['user_id']

def isFollowingProfile(user_id):
    if 'loggedin' not in session or user_id == None:
        return False
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM follows WHERE following_id = %s and follower_id = %s', (user_id, session['id'],))
    flag = cursor.fetchone()
    cursor.close()
    if flag != None:
        return True
    return False

def editProfile(username, description):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE user SET username=%s, user_desc=%s WHERE user_id = %s ', (username, description, session['id'],))
    cursor.close()
    mysql.connection.commit()
    flash('You have updated your username and description successfully', 'success')
    return

def toggleFollow(user_id, target_id):
    if user_id and user_id != 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM follows WHERE follower_id = %s AND following_id = %s', (user_id, target_id,))
        result = cursor.fetchall()
        if result is None or len(result) == 0:
            cursor.execute('INSERT INTO follows VALUES (%s, %s)', (user_id, target_id,))
        else:
            cursor.execute('DELETE FROM follows WHERE follower_id = %s AND following_id = %s', (user_id, target_id))
        cursor.close()
        mysql.connection.commit()
    else:
        flash('You need to log in before following!')
    return

def getUserNames():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT username FROM user')
    query_result = cursor.fetchall()
    cursor.close()
    usernames = []
    for i in query_result:
        usernames.append((i['username']))
    return usernames

# RECIPES

recipe_per_page = 9
saved_recipe_query_data = None

def newRecipeSearchQuery(query):
    user_inventory = 0
    if 'loggedin' in session and query['my_ingredients']:
        user_inventory = session['id']
    query_name = '%'
    tokens = query['text'].split(" ")
    for token in tokens:
        if token != '':
            query_name = query_name + token + '%'
    dietary = ''
    for i in query['dietary']:
        dietary += i
        if i != query['dietary'][-1]:
            dietary += ','
    user_bookmark = 0
    if 'loggedin' in session and query['bookmarked']:
        user_bookmark = session['id']
    cuisine = ''
    for i in query['cuisine']:
        cuisine += i
        if i != query['cuisine'][-1]:
            cuisine += ','

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.callproc('search_procedure', (query_name, query['creator_id'], query['ingredient'], dietary,
                                         user_inventory, user_bookmark, cuisine, query['sort_attribute'], query['sort_direction'],))
    query_data = cursor.fetchall()
    cursor.close()

    for recipe in query_data:
        if recipe['cuisines']:
            recipe['cuisines'] = recipe['cuisines'].split(',')
        else:
            recipe['cuisines'] = []
    return query_data

def getSavedRecipeQueryData():
    return saved_recipe_query_data

# creates new recipe, stores basic information, returns id
def newRecipe(creator_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/SNice.svg/220px-SNice.svg.png'
    cursor.execute('INSERT INTO recipe VALUES (NULL, %s, %s, %s, NULL, NULL, NULL, %s, %s, NULL)',
                    ('New Recipe Name', 'New Recipe Description', url, creator_id, datetime.datetime.now().date(),))
    return_id = cursor.lastrowid
    cursor.close()
    mysql.connection.commit()
    
    return return_id

def deleteRecipe(recipe_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM recipe WHERE recipe_id=%s', (recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def getRecipeInfoFromRecipeId(recipe_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT R.*, username as creator_username FROM recipe R, user WHERE recipe_id = %s AND creator_id = user_id', (recipe_id,))
    recipe = cursor.fetchone()
    if recipe is None:
        return None

    cursor.execute('SELECT instr_id, title, subtitle, list_order FROM instruction WHERE recipe_id = %s ORDER BY list_order', (recipe_id,))
    recipe['instructions'] = cursor.fetchall()
    cursor.execute('SELECT I.ingr_id, ingr_name, quantity FROM ingredient I, uses_ingredient U WHERE recipe_id = %s AND I.ingr_id = U.ingr_id', (recipe_id,))
    recipe['ingredients'] = cursor.fetchall()
    cursor.execute('SELECT cuisine_id, tag_name FROM belongs_to, tag WHERE recipe_id = %s AND cuisine_id = tag_id', (recipe_id,))
    recipe['cuisines'] = cursor.fetchall()
    
    ingredient_list = []
    for i in recipe['ingredients']:
        ingredient_list.append(i['ingr_id'])
    if len(ingredient_list) == 0:
        ingredient_list.append('')
    cursor.execute('SELECT tag_id, tag_name FROM tag WHERE tag_id NOT IN (SELECT dietary_id FROM excludes WHERE ingr_id IN %s) AND tag_id NOT IN (SELECT tag_id FROM cuisine)', (ingredient_list,))
    recipe['dietary'] = cursor.fetchall()
    
    cursor.execute('SELECT AVG(score) as score FROM rating WHERE recipe_id = %s', (recipe_id,))
    recipe['rating'] = cursor.fetchone()['score']
    
    cursor.close() 
    return recipe

def editRecipeName(recipe_id, name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE recipe SET recipe_name=%s WHERE recipe_id = %s ', (name, recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def editRecipeDescription(recipe_id, description):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE recipe SET recipe_desc=%s WHERE recipe_id = %s ', (description, recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def editRecipeImage(recipe_id, image):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE recipe SET recipe_image=%s WHERE recipe_id = %s ', (image, recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def editRecipePortions(recipe_id, portions):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE recipe SET portions=%s WHERE recipe_id = %s ', (portions, recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def editRecipeDuration(recipe_id, duration):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE recipe SET duration=%s WHERE recipe_id = %s ', (duration, recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def editRecipeDifficulty(recipe_id, difficulty):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('UPDATE recipe SET difficulty=%s WHERE recipe_id = %s ', (difficulty, recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def addRecipeIngredient(recipe_id, ingr_id, quantity):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO uses_ingredient VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE quantity=VALUES(quantity)', (ingr_id, recipe_id, quantity,))
    cursor.close()
    mysql.connection.commit()
    return

def deleteRecipeIngredient(recipe_id, ingr_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM uses_ingredient WHERE recipe_id=%s AND ingr_id=%s', (recipe_id, ingr_id,))
    cursor.close()
    mysql.connection.commit()
    return

def addRecipeInstruction(recipe_id, title, subtitle):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT MAX(instr_id) as curmax, COUNT(*) as count FROM instruction WHERE recipe_id=%s', (recipe_id,))
    query_result = cursor.fetchone()
    if query_result == None:
        curmax = 0
        count = 0
    else:
        curmax = query_result['curmax']
        count = query_result['count']
        if curmax == None:
            curmax = 0
        if count == None:
            count = 0
    
    cursor.execute('INSERT INTO instruction VALUES(%s, %s, %s, %s, %s)', (recipe_id, curmax + 1, title, subtitle, count + 1))
    cursor.close()
    mysql.connection.commit()
    return

def deleteRecipeInstruction(recipe_id, instr_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT list_order FROM instruction WHERE recipe_id=%s AND instr_id=%s', (recipe_id, instr_id,))
    query_result = cursor.fetchone()
    if query_result == None:
        return
    removed_index = query_result['list_order']
    cursor.callproc('del_instr', (recipe_id, instr_id, removed_index))
    cursor.close()
    mysql.connection.commit()
    return

def upRecipeInstruction(recipe_id, instr_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM instruction WHERE recipe_id=%s AND instr_id=%s', (recipe_id, instr_id,))
    instruction = cursor.fetchone()
    if instruction == None:
        return
    index = instruction['list_order'] - 1
    cursor.execute('SELECT * FROM instruction WHERE recipe_id=%s AND list_order=%s', (recipe_id, index,))
    instruction = cursor.fetchone()
    if instruction == None:
        return
    lower_instr_id = instruction['instr_id']

    cursor.callproc('swap_instr', (recipe_id, lower_instr_id, index,))
    cursor.close()
    mysql.connection.commit()
    return

def downRecipeInstruction(recipe_id, instr_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM instruction WHERE recipe_id=%s AND instr_id=%s', (recipe_id, instr_id,))
    instruction = cursor.fetchone()
    if instruction == None:
        return
    index = instruction['list_order']

    cursor.callproc('swap_instr', (recipe_id, instr_id, index,))
    cursor.close()
    mysql.connection.commit()
    return

def editRecipeCuisineTags(recipe_id, cuisine_tags): # cuisine tags is a list of (id, add (1) or remove (-1))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    for cuisine in cuisine_tags:
        if cuisine[1] == 1:
            cursor.execute('INSERT INTO belongs_to VALUES (%s, %s)', (recipe_id, cuisine[0],))
        else:
            cursor.execute('DELETE FROM belongs_to WHERE recipe_id=%s AND cuisine_id=%s', (recipe_id, cuisine[0],))
    cursor.close()
    mysql.connection.commit()
    return

def getRecipeRatings(recipe_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT COUNT(*) AS count, score FROM rating WHERE recipe_id = %s GROUP BY score', (recipe_id,))
    result = cursor.fetchall()
    ratings = [0, 0, 0, 0, 0]
    for i in result:
        ratings[int(i['score'])-1] = i['count']
    cursor.close()
    return ratings

def getUserRating(recipe_id):
    if 'loggedin' not in session:
        return None
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT score FROM rating WHERE user_id=%s AND recipe_id = %s', (session['id'], recipe_id,))
    result = cursor.fetchone()
    cursor.close()
    if result == None:
        return None
    return result['score']

def updateRating(user_id, recipe_id, rating):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO rating VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE score=VALUES(score)', (user_id, recipe_id, rating,))
    cursor.close()
    mysql.connection.commit()
    return

def removeRating(user_id, recipe_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM rating WHERE user_id = %s AND recipe_id = %s', (user_id, recipe_id,))
    cursor.close()
    mysql.connection.commit()
    return

def toggleBookmark(user_id, target_id):
    if user_id and user_id != 0:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM bookmark WHERE user_id = %s AND recipe_id = %s', (user_id, target_id,))
        result = cursor.fetchall()
        if result is None or len(result) == 0:
            cursor.execute('INSERT INTO bookmark VALUES (%s, %s)', (user_id, target_id,))
        else:
            cursor.execute('DELETE FROM bookmark WHERE user_id = %s AND recipe_id = %s', (user_id, target_id))
        cursor.close()
        mysql.connection.commit()
    else:
        flash('You need to log in before bookmarking!')
    return

def bookmarkedRecipe(recipe_id):
    if 'loggedin' not in session or recipe_id == None:
        return False
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM bookmark WHERE user_id = %s and recipe_id = %s', (session['id'], recipe_id,))
    flag = cursor.fetchone()
    cursor.close()
    if flag != None:
        return True
    return False

def getCuisineTags():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT T.tag_id, T.tag_name FROM cuisine C, tag T WHERE C.tag_id = T.tag_id ORDER BY C.region, C.subregion, T.tag_name')
    query_result = cursor.fetchall()
    cursor.close()
    cuisine_tags = []
    for i in query_result:
        cuisine_tags.append((i['tag_id'], i['tag_name']))
    return cuisine_tags

def getDietaryTags():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT DISTINCT T.tag_id, T.tag_name FROM excludes E, tag T where E.dietary_id = T.tag_id ORDER BY T.tag_name')
    query_result = cursor.fetchall()
    cursor.close()
    dietary_tags = []
    for i in query_result:
        dietary_tags.append((i['tag_id'], i['tag_name']))
    return dietary_tags

# INVENTORY

def getInventoryOfUser(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT V.*, ingr_name FROM inventory V, ingredient I WHERE user_id=%s AND V.ingr_id=I.ingr_id', (user_id,))
    query_result = cursor.fetchall()
    cursor.close()
    return query_result

def addIngredientToInventory(user_id, ingredient_id, expiry_date):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM inventory WHERE user_id=%s AND ingr_id=%s AND expiry=%s', (user_id, ingredient_id, expiry_date,))
    result = cursor.fetchone()
    if result == None:
        cursor.execute('INSERT INTO inventory VALUES (%s, %s, %s)', (user_id, ingredient_id, expiry_date,))
    cursor.close()
    mysql.connection.commit()
    return

def removeIngredientFromInventory(user_id, ingredient_id, expiry_date):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM inventory WHERE user_id=%s AND ingr_id=%s AND expiry=%s', (user_id, ingredient_id, expiry_date,))
    cursor.close()
    mysql.connection.commit()
    return

def getIngredientNames():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT ingr_name FROM ingredient')
    query_result = cursor.fetchall()
    cursor.close()
    names = []
    for i in query_result:
        names.append((i['ingr_name']))
    return names

def getIngredientIdFromIngredientName(name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT ingr_id FROM ingredient WHERE ingr_name=%s', (name,))
    query_result = cursor.fetchone()
    cursor.close()
    if query_result == None:
        return None
    return query_result['ingr_id']

# FEEDBACK

def storeFeedback(feedback_text):
    # this is actually how council works
    flash('Your feedback has been submitted!', 'success')
    return