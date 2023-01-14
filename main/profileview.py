from flask import flash, url_for, session, redirect, render_template, request
from forms import EditProfileForm
import tools

def profile(user_id):
    userinfo = tools.getCurrentUserInfo()
    profileinfo = tools.getUserInfoFromUserId(user_id)
    if profileinfo == None:
        flash('Page could not be found!', 'warning')
        return redirect('/')
        

    form = EditProfileForm()

    result = request.form
    if 'form_name' in result and result['form_name'] == 'toggle-follow':
            tools.toggleFollow(userinfo['user_id'], profileinfo['user_id'])
            userinfo = tools.getCurrentUserInfo()
            profileinfo = tools.getUserInfoFromUserId(user_id)
    elif form.is_submitted():
        if form.profile_submit.data and form.validate():
            username = result['profile_username']
            description = result['profile_description']
            checkUser = tools.getUserInfoFromUsername(username)
            if checkUser != None:
                flash('Username already taken! Please try again', 'danger')
            else:
                tools.editProfile(user_id, username, description)
        else:
            flash('Profile editing failed. Please try again.', 'danger')
        

    return render_template('profile.html', userinfo=userinfo, profileinfo=profileinfo, form=form, currentPage='profile')

''' {{ toggle_follow_form.toggle_follow(class_="btn btn-unfollow bi", value="Unfollow &#xF586;") }}
    <button class="btn btn-unfollow">
        Unfollow
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-star-fill ms-1" viewBox="0 0 16 16">
            <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
        </svg>
    </button>'''