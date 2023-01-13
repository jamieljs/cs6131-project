from flask import session
import hashlib, uuid
import copy

# LOGIN / USERS

def hashPassword(password, salt):
    salted = password + salt
    return hashlib.sha512(salted.encode('utf-8')).hexdigest()

user_list = [{'user_id': 0, 'user_username': 'username', 'user_password': hashPassword('password', 'salt'), 'user_salt': 'salt', 'user_description': 'Hello there! I enjoy cooking :)'}, {'user_id': 1, 'user_username': 'user2', 'user_password': hashPassword('password', 'salt'), 'user_salt': 'salt', 'user_description': 'Hello there! I enjoy cooking :)'}]

def login(user_info):
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed

def getCurrentUserInfo():
    try:
        user_id =  dict(session)['profile']['user_id']
        user_info =  getUserInfoFromUserId(user_id)
        return user_info
    except KeyError as e:
        return None
    return None

def getUserInfoFromUserId(user_id):
    if not isinstance(user_id, int) or user_id < 0 or user_id >= len(user_list):
        return None
    return user_list[user_id]

def getUserInfoFromUsername(username):
    for i in range(len(user_list)):
        if user_list[i]['user_username'] == username:
            return user_list[i]
    return None

def checkPassword(userinfo, password):
    return (userinfo['user_password'] == hashPassword(password, userinfo['user_salt']))

def createUser(username, password):
    salt = uuid.uuid4().hex
    userinfo = {'user_id': len(user_list),
                'user_username': username,
                'user_password': hashPassword(password, salt),
                'user_salt': salt,
                'user_description': ''}
    user_list.append(userinfo)
    return userinfo

def editProfile(user_id, username, description):

    return 0

def toggleFollow(user_id, target_id):
    pass

# RECIPES

recipe_tags = [('vgt', 'Vegetarian'), ('vgn', 'Vegan'), ('egg', 'Egg-Free'), ('nut', 'Nut-Free'), ('dai', 'Dairy-Free'), ('glu', 'Gluten-Free'), ('flr', 'Flour-Less')]
recipe_list = [{'recipe_id': 0, 'recipe_name': 'Sample Recipe', 'recipe_description': 'some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text', 'recipe_instructions': [('heading', 'some long text some long text some long text some long text some long text some long text'), ('second instruction', 'texttext')], 'recipe_difficulty': 0, 'recipe_cook_time': 0.5, 'recipe_privacy': False, 'recipe_image': 'https://github.com/jamieljs.png', 'recipe_creator': 0},
               {'recipe_id': 1, 'recipe_name': 'Sample Recipe', 'recipe_description': 'some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text', 'recipe_instructions': [('heading', 'some long text some long text some long text some long text some long text some long text'), ('second instruction', 'texttext')], 'recipe_difficulty': 0, 'recipe_cook_time': 0.5, 'recipe_privacy': True, 'recipe_image': 'https://github.com/dvdg6566.png', 'recipe_creator': 1},
               {'recipe_id': 2, 'recipe_name': 'Sample Recipe', 'recipe_description': 'some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text', 'recipe_instructions': [('heading', 'some long text some long text some long text some long text some long text some long text'), ('second instruction', 'texttext')], 'recipe_difficulty': 1, 'recipe_cook_time': 0.5, 'recipe_privacy': False, 'recipe_image': 'https://github.com/jamieljs.png', 'recipe_creator': 0},
               {'recipe_id': 3, 'recipe_name': 'Sample Recipe', 'recipe_description': 'some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text some long text', 'recipe_instructions': [('heading', 'some long text some long text some long text some long text some long text some long text'), ('second instruction', 'texttext')], 'recipe_difficulty': 2, 'recipe_cook_time': 3, 'recipe_privacy': False, 'recipe_image': 'https://github.com/dvdg6566.png', 'recipe_creator': 1}]
cuisine_tags = [('caf', 'Central African'), ('eaf', 'East African'), ('naf', 'North African'), ('saf', 'Southern African'), ('waf', 'West African'), ('nam', 'North American'), ('cam', 'Central American'), ('sam', 'South American'), ('car', 'Caribbean'), ('cas', 'Central Asian'), ('eas', 'East Asian'), ('sas', 'South Asian'), ('sea', 'Southeast Asian'), ('was', 'West Asian'), ('ceu', 'Central European'), ('eeu', 'Eastern European'), ('neu', 'Northern European'), ('seu', 'Southern European'), ('weu', 'Western European'), ('oce', 'Oceanic')]

recipe_per_page = 12
saved_recipe_query_data = None

def newRecipeSearchQuery(form_data):
    if form_data:
        if 'search_creator_id' in form_data and form_data['search_creator_id'] != -1:
            pass
        else:
            pass

        if 'search_bookmarked' in form_data and form_data['search_bookmarked'] == 1:
            pass
        else:
            pass
        temp_query_data = copy.deepcopy(recipe_list)
        # TODO: query based on form data
    else:
        temp_query_data = copy.deepcopy(recipe_list)

    saved_recipe_query_data = []

    for recipe in temp_query_data:
        if len(recipe['recipe_description']) > 100:
            recipe['recipe_description'] = recipe['recipe_description'][:100] + '[...]'
        recipe.pop('recipe_instructions')
        saved_recipe_query_data.append(recipe)
        
    return saved_recipe_query_data

def getSavedRecipeQueryData():
    return saved_recipe_query_data

# creates new recipe, stores basic information, returns id
def newRecipe(creator_id):
    return_id = len(recipe_list)
    recipe_list.append({'recipe_id':return_id, 'recipe_name':'Placeholder Recipe Name', 'recipe_description':'', 'recipe_instructions': [], 'recipe_difficulty': 0, 'recipe_cook_time': 0.5, 'recipe_privacy': False, 'recipe_image': 'https://github.com/jamieljs.png', 'recipe_creator':creator_id})
    return return_id

def deleteRecipe(recipe_id):
    return None

def editRecipe(recipe_id):
    return None

def getRecipeInfoFromRecipeId(recipe_id):
    # TODO: there is more to be done (merging from other tables) but recipe_list is overpowered for now
    return recipe_list[recipe_id]

def toggleBookmark(user_id, target_id):
    pass

# INVENTORY

import datetime

def getInventoryOfUser(user_id):
    return [{'ingredient_id':0,'ingredient_name':'sample ingredient 0','expiry_date':datetime.datetime.now().date()}, {'ingredient_id':1,'ingredient_name':'sample ingredient 1','expiry_date':datetime.datetime.now().date() - datetime.timedelta(days=1)}, {'ingredient_id':2,'ingredient_name':'sample ingredient 2','expiry_date':datetime.datetime.now().date() + datetime.timedelta(days=1)}]

def addIngredientToInventory(user_id, ingredient_id, expiry_date):
    '''if exists, dont add'''
    pass

def removeIngredientFromInventory(user_id, ingredient_id, expiry_date):
    '''if doesnt exist, do nothing'''
    pass

def getIngredientNames():
    return ['food1', 'kajdns', 'iaehc', 'fadsfjjncksjn4']
