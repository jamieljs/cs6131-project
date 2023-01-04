from flask import flash, render_template, session, request, redirect
from forms import LoginForm, RegisterForm
import tools

def login():
    userinfo = tools.getCurrentUserInfo()
    if userinfo != None and userinfo['user_id'] != '':
        flash('Please log out before trying to log in!', 'warning')
        return redirect('/')
    loginForm = LoginForm()
    registerForm = RegisterForm()

    if loginForm.validate_on_submit() and loginForm.login.data:
        result = request.form
        username = result['username']
        password = result['password']
        checkUser = tools.getUserInfoFromUsername(username)
        if checkUser != None:
            if checkUser['user_username'] == username and checkUser['user_password'] == password:
                tools.login(checkUser)
                flash('Welcome back, ' + str(username) + '!', 'success')
                return redirect('/home')
        flash('Login failed. Please try again.', 'error')
        return redirect('/login')
    elif registerForm.validate_on_submit() and registerForm.register.data:
        result = request.form
        username = result['username']
        email = result['email']
        password = result['password']
        confirm_password = result['confirm_password']
        checkUser = tools.getUserInfoFromUsername(username)
        if checkUser == None:
            checkUserEmail = tools.checkEmailExists(email)
            if checkUserEmail:
                flash('This email address already has an associated account. Please try again', 'error')
                return redirect('/login#register')
            else:
                if tools.isValidPassword(password):
                    tools.login(tools.createUser(username, email, password))
                    flash('Welcome, ' + str(username) + '!', 'success')
                    return redirect('/home')
        else:
            flash('This username is taken. Please try again.', 'error')
            return redirect('/login#register')
        flash('Registration failed. Please try again.', 'error')
        return redirect('/login#register')

    return render_template('login.html', loginForm = loginForm, registerForm = registerForm)