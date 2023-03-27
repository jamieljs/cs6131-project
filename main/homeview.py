from flask import flash, url_for, session, redirect, render_template, request
import tools

def home():
    return render_template('home.html', username_input = None)