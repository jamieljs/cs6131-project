from flask import flash, redirect, render_template, url_for
from forms import FeedbackForm
import tools

def feedback():
    userinfo = tools.getCurrentUserInfo()
    form = FeedbackForm()

    if form.validate_on_submit():
        ''' TODO: actually store the feedback or something '''
        flash('Your feedback has been received!', 'success')
        redirect('/')

    return render_template('feedback.html', userinfo = userinfo, form = form, currentPage = 'feedback')
