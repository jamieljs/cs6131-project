from flask import flash, url_for, session, redirect, render_template, request
from forms import FeedbackForm
import tools

def feedback():
    form = FeedbackForm()

    if form.validate_on_submit():
        tools.storeFeedback(request.form['feedback_text'])
        return redirect('/')

    return render_template('feedback.html', form = form)
