from flask import flash, url_for, session, redirect, render_template, request
import tools

def home():
    userinfo = tools.getCurrentUserInfo()
    return render_template('home.html', userinfo = userinfo, currentPage = 'home')