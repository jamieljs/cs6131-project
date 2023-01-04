from flask import session

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
    return None

def getUserInfoFromUsername(user_id):
    return None

def checkEmailExists(email):
    return False

def isValidPassword(password):
    return True

def createUser(username, email, password):
    userinfo = {}
    return userinfo
