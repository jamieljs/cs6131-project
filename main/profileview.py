from flask import flash, url_for, session, redirect, render_template, request
from forms import EditProfileForm
import tools

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
    elif 'form_name' in result and result['form_name'] == 'toggle-follow':
        tools.toggleFollow(session['id'], profileinfo['user_id'])
        profileinfo = tools.getProfileInfoFromUserId(user_id)
    
    return render_template('profile.html', user_is_following_profile=tools.isFollowingProfile(user_id), profileinfo=profileinfo, form=form)