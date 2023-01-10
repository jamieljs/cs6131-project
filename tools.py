from flask import session
import hashlib, uuid

user_list = []
recipe_tags = ['Vegetarian', 'Vegan', 'Egg-Free', 'Nut-Free', 'Dairy-Free', 'Gluten-Free', 'Spicy']
recipe_list = []


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
    return user_list[user_id]

def getUserInfoFromUsername(username):
    for i in range(len(user_list)):
        if user_list[i]['user_username'] == username:
            return user_list[i]
    return None

def checkEmailExists(email):
    for i in range(len(user_list)):
        if user_list[i]['user_email'] == email:
            return True
    return False

def checkPassword(userinfo, password):
    return (userinfo['user_password'] == hashPassword(password, userinfo['user_salt']))

def hashPassword(password, salt):
    return hashlib.sha512(password + salt).hexdigest()

def createUser(username, email, password):
    salt = uuid.uuid4().hex
    userinfo = {'user_id': len(user_list),
                'user_username': username,
                'user_password': hashPassword(password, salt),
                'user_salt': salt,
                'user_email': email,
                'user_description': ''}
    user_list.append(userinfo)
    return userinfo

recipe_per_page = 10
saved_query_data = recipe_list

def newSearchQuery(form_data):
    if form_data == None:
        saved_query_data = recipe_list
    else:
        saved_query_data = []
        # return based on data
    return saved_query_data

def getSavedQueryData():
    return saved_query_data