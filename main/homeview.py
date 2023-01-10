from flask import flash, render_template, url_for
import tools

def home():
    userinfo = tools.getCurrentUserInfo()
    return render_template('home.html', userinfo = userinfo, currentPage = 'home')