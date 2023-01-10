from flask import flash, render_template, session, request, redirect, url_for
from forms import LoginForm, RegisterForm
import tools

def login():
    userinfo = tools.getCurrentUserInfo()
    if userinfo != None and userinfo['user_id'] != '':
        flash('Please log out before trying to log in!', 'warning')
        return redirect('/')
    loginForm = LoginForm()
    registerForm = RegisterForm()

    if loginForm.is_submitted() and loginForm.login.data:
        if loginForm.validate():
            result = request.form
            username = result['username']
            password = result['password']
            checkUser = tools.getUserInfoFromUsername(username)
            if checkUser != None:
                if checkUser['user_username'] == username and tools.checkPassword(checkUser, password):
                    tools.login(checkUser)
                    flash('Welcome back, ' + str(username) + '!', 'success')
                    return redirect('/')
        flash('Login failed. Please try again.', 'danger')
        return render_template('login.html', loginForm = loginForm, registerForm = registerForm, pageType='login')
    elif registerForm.is_submitted() and registerForm.register.data:
        if registerForm.validate():
            result = request.form
            username = result['reg_username']
            email = result['reg_email']
            password = result['reg_password']
            checkUser = tools.getUserInfoFromUsername(username)
            if checkUser == None:
                checkUserEmail = tools.checkEmailExists(email)
                if checkUserEmail:
                    flash('This email address already has an associated account. Please try again', 'danger')
                    return render_template('login.html', loginForm = loginForm, registerForm = registerForm, pageType='register')
                else:
                    tools.login(tools.createUser(username, email, password))
                    flash('Welcome, ' + str(username) + '!', 'success')
                    return redirect('/')
            else:
                flash('This username is taken. Please try again.', 'danger')
                return render_template('login.html', loginForm = loginForm, registerForm = registerForm, pageType='register')
        flash('Registration failed. Please try again.', 'danger')
        return render_template('login.html', loginForm = loginForm, registerForm = registerForm, pageType='register')
        
    return render_template('login.html', loginForm = loginForm, registerForm = registerForm, pageType='login')