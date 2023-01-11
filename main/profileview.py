from flask import flash, url_for, redirect, render_template, request
from forms import EditProfileForm
import tools

def profile(user_id):
    userinfo = tools.getCurrentUserInfo()
    profileinfo = tools.getUserInfoFromUserId(user_id)
    if profileinfo == None:
        flash('Page could not be found!', 'warning')
        redirect('/')

    form = EditProfileForm()
    
    if form.is_submitted() and form.profile_submit.data:
        if form.validate():
            result = request.form
            username = result['profile_username']
            description = result['profile_description']
            email = result['profile_email']
            checkUser = tools.getUserInfoFromUsername(username)
            checkEmail = tools.checkEmailExists(email)
            if checkUser != None:
                flash('Username already taken! Please try again', 'danger')
            elif checkEmail:
                flash('Email already assigned to another account! Please try again', 'danger')
                # currently ignoring the case where other people accidentally/purposely use your email
            else:
                tools.editProfile(user_id, username, description, email)
        else:
            flash('Profile editing failed. Please try again.', 'danger')

    return render_template('profile.html', userinfo=userinfo, profileinfo=profileinfo, form=form, currentPage='profile')