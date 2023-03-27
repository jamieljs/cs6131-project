from flask import flash, render_template, session, request, redirect, url_for
from forms import LoginForm, RegisterForm
import tools

def login():
    if 'loggedin' in session:
        flash('Please log out before trying to log in!', 'warning')
        return redirect('/')
    loginForm = LoginForm()
    registerForm = RegisterForm()

    if loginForm.is_submitted() and loginForm.login.data:
        if loginForm.validate():
            result = request.form
            if tools.login(result['username'], result['password']):
                return redirect('/')
        else:
            flash('Login failed. Please try again.', 'danger')
    elif registerForm.is_submitted() and registerForm.login.data:
        if registerForm.validate():
            result = request.form
            username = result['reg_username']
            password = result['reg_password']
            if tools.register(username, password):
                return redirect('/')
        else:
            flash('Registration failed. Please try again.', 'danger')
        return render_template('login.html', loginForm = loginForm, registerForm = registerForm, pageType='register')

    return render_template('login.html', loginForm = loginForm, registerForm = registerForm, pageType='login')