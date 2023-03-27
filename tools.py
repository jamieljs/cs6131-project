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
    if isValidUsername(username):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, NULL)', (username, generate_password_hash(password),))
        cursor.close()
        mysql.connection.commit() #commit the insertion
        login(username, password)
        return True
    return False

def getProfileInfoFromUserId(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE user_id = %s', (user_id,))
    account = cursor.fetchone()
    cursor.execute('SELECT follower_id, username FROM follows, user WHERE following_id = %s and follower_id = user_id', (user_id,))
    account['followers'] = cursor.fetchall()
    cursor.execute('SELECT following_id, username FROM follows, user WHERE follower_id = %s and following_id = user_id', (user_id,))
    account['following'] = cursor.fetchall()
    cursor.close()
    return account

def isValidUsername(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
    account = cursor.fetchone()
    
    if account:
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
    cursor.execute('UPDATE user set username=%s, user_desc=%s WHERE user_id = %s ', (username, description, session['id'],))
    cursor.close()
    mysql.connection.commit()
    flash('You have updated your username and description successfully', 'success')
    return

def toggleFollow(user_id, target_id):
    pass

def getUserNames():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT username FROM user')
    usernames = cursor.fetchall()
    cursor.close()
    return usernames

# RECIPES

recipe_per_page = 12
saved_recipe_query_data = None

''' TODO: make this a stored procedure if possible because this code is ugly '''
def newRecipeSearchQuery(query):
    query_name = '%'
    tokens = query['text'].split(" ")
    for token in tokens:
        if token != '':
            query_name = query_name + token + '%'
    if query['dietary'] == []:
        query['dietary'] = ['']
    if query['cuisine'] == []:
        query['cuisine'] = ['']
    
    query_prefix =   '''SELECT id, name, description, image, duration, difficulty, rating, cuisines
                        FROM
                            ( 
                            SELECT recipe_id AS id, recipe_name AS name,
                                CASE
                                    WHEN LENGTH(recipe_desc) > 100 THEN CONCAT(LEFT(recipe_desc, 100), '[...]')
                                    ELSE recipe_desc
                                END AS description,
                                recipe_image AS image, cook_time AS duration, difficulty, recipe_rating AS rating
                                FROM recipe R
                                WHERE recipe_name LIKE %s
                                  AND (%s = 0 OR creator_id = %s)
                                  AND recipe_id IN (
                                                   SELECT recipe_id
                                                   FROM uses_ingredient U, ingredient I
                                                   WHERE U.ingr_id = I.ingr_id AND (%s = '' OR I.ingr_name = %s)
                                                   )
                                  AND recipe_id NOT IN (
                                                       SELECT recipe_id
                                                       FROM uses_ingredient U, excludes E
                                                       WHERE U.ingr_id = E.ingr_id AND E.dietary_id IN %s
                                                       )'''
    if 'loggedin' in session and query['my_ingredients']:
        query_inventory =      '''AND recipe_id NOT IN (
                                                       SELECT recipe_id
                                                       FROM uses_ingredient U, inventory I
                                                       WHERE U.ingr_id IN (
                                                                          SELECT ingr_id
                                                                          FROM inventory WHERE user_id = ''' + session['id'] + '''
                                                                          GROUP BY ingr_id HAVING MAX(expiry) < CURDATE()
                                                                          ) OR
                                                             U.ingr_id NOT IN (SELECT ingr_id FROM inventory WHERE user_id = ''' + session['id'] + '))'
    else:
        query_inventory = ''
    if 'loggedin' in session and query['bookmarked']:
        query_bookmarked =       'AND recipe_id IN (SELECT recipe_id FROM bookmark WHERE user_id = ' + session['id'] + ')'
    else:
        query_bookmarked = ''
    query_suffix = '''            AND (%s IN ('') OR (
                                                     SELECT COUNT(*)
                                                     FROM belongs_to B, tag T
                                                     WHERE R.recipe_id = B.recipe_id AND B.cuisine_id = T.tag_id and T.tag_id IN %s
                                                     ) > 0
                                      )
                            ) T1
                            NATURAL LEFT JOIN
                            (
                            SELECT R.recipe_id AS id, GROUP_CONCAT(T.tag_name) AS cuisines
                            FROM recipe R, belongs_to B, tag T
                            WHERE R.recipe_id = B.recipe_id AND B.cuisine_id = T.tag_id
                            GROUP BY R.recipe_id
                            ) T2
                        ORDER BY %s %s'''
    
    query_string = query_prefix + query_inventory + query_bookmarked + query_suffix
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query_string, (query_name,
                                  query['creator_id'], query['creator_id'],
                                  query['ingredient'], query['ingredient'],
                                  query['dietary'],
                                  query['cuisine'], query['cuisine'],
                                  query['sort_attribute'], query['sort_direction'],))
    saved_recipe_query_data = cursor.fetchall()
    cursor.close()

    print(saved_recipe_query_data)
    for recipe in saved_recipe_query_data:
        if recipe['cuisines']:
            recipe['cuisines'] = recipe['cuisines'].split(',')
        else:
            recipe['cuisines'] = []
    return saved_recipe_query_data

def getSavedRecipeQueryData():
    return saved_recipe_query_data

# creates new recipe, stores basic information, returns id
def newRecipe(creator_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO recipe VALUES (NULL, %s, %s, NULL, NULL, NULL, NULL, %s, %s, NULL)',
                    ('New Recipe Name', 'New Recipe Description', creator_id, datetime.datetime.now().date(),))
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

def editRecipe(recipe_id):
    return None

def getRecipeInfoFromRecipeId(recipe_id):
    # TODO
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM recipe WHERE recipe_id = %s', (recipe_id,))
    recipe = cursor.fetchone()

    recipe['instructions'] = []

    recipe['ingredients'] = []

    recipe['cuisines'] = []

    recipe['dietary'] = []

    recipe['rating'] = []

    cursor.close() 
    return recipe

def getRecipeRatings(recipe_id):
    return [1, 1, 0, 0, 0]

def updateRating(user_id, recipe_id, rating):
    pass

def toggleBookmark(user_id, target_id):
    pass

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
    cursor.execute('SELECT T.tag_id, T.tag_name FROM cuisine C, tag T WHERE C.tag_id = T.tag_id')
    query_result = cursor.fetchall()
    cursor.close()
    cuisine_tags = []
    for i in query_result:
        cuisine_tags.append((i['tag_id'], i['tag_name']))
    return cuisine_tags

def getDietaryTags():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT T.tag_id, T.tag_name FROM excludes E, tag T where E.dietary_id = T.tag_id')
    query_result = cursor.fetchall()
    cursor.close()
    dietary_tags = []
    for i in query_result:
        dietary_tags.append((i['tag_id'], i['tag_name']))
    return dietary_tags

# INVENTORY

def getInventoryOfUser(user_id):
    return [{'ingredient_id':0,'ingredient_name':'sample ingredient 1','expiry_date':datetime.datetime.now().date()}, {'ingredient_id':1,'ingredient_name':'sample ingredient 2','expiry_date':datetime.datetime.now().date() - datetime.timedelta(days=1)}, {'ingredient_id':2,'ingredient_name':'food','expiry_date':datetime.datetime.now().date() + datetime.timedelta(days=1)}]

def addIngredientToInventory(user_id, ingredient_id, expiry_date):
    '''if exists, dont add'''
    pass

def removeIngredientFromInventory(user_id, ingredient_id, expiry_date):
    '''if doesnt exist, do nothing'''
    pass

def getIngredientNames():
    return ['sample ingredient 1', 'sample ingredient 2', 'food', 'abc', 'def', 'ghi', 'jkl']

# FEEDBACK

def storeFeedback(feedback_text):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO feedback VALUES (NULL, %s)', (feedback_text,))
    cursor.close()
    mysql.connection.commit() #commit the insertion
    flash('Your feedback has been submitted!', 'success')
    return