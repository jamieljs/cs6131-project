from flask import flash, url_for, session, redirect, render_template, request
from forms import EditProfileForm
import tools

def togglefollowprofile():
    if 'loggedin' in session:
        userid = session['id']
    else:
        return {'status':300,'error':'Access to resource denied'}

    target_id = request.form['target_id']
    if target_id:
        tools.toggleFollow(userid, target_id)
        return {'status':200,'error':''}

    return {'status':300,'error':'Access to resource denied'}

def profile(user_id):
    profileinfo = tools.getProfileInfoFromUserId(user_id)
    if profileinfo == None:
        flash('Page could not be found!', 'warning')
        return redirect('/')
        
    form = EditProfileForm()

    result = request.form
    if form.is_submitted() and form.profile_submit.data:
        if form.validate():
            username = result['profile_username']
            description = result['profile_description']
            if tools.isValidUsername(username):
                tools.editProfile(username, description)
                profileinfo = tools.getProfileInfoFromUserId(user_id)
        else:
            flash('Profile editing failed. Please try again.', 'danger')

    return render_template('profile.html', user_is_following_profile=tools.isFollowingProfile(user_id), profileinfo=profileinfo, form=form)