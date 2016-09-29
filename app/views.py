from flask import render_template, flash, redirect, url_for, session, send_from_directory, send_file, Response, g
from werkzeug.utils import secure_filename
from app import app, db, lm
from .forms import CreateImageForm
from .models import User

import numpy as np
import scipy.misc
from PIL import Image
import time
from io import BytesIO
import base64

import make_image

from oauth import OAuthSignIn
from flask.ext.login import login_user, current_user, login_required

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/upload_images', methods=('GET', 'POST'))
@login_required
def upload_images():
	form = CreateImageForm()
	if form.validate_on_submit():
		filename = secure_filename(form.style_im.data.filename)
		form.style_im.data.save('uploads/' + filename)
		session['style_im'] = filename
		session['num_iters'] = form.num_iter.data
		return redirect(url_for('create_image'))
	return render_template('upload_images.html', form=form)

@app.route('/uploads/<filename>')
def send_image(filename):
	return send_from_directory('../uploads/', filename)

@app.route('/out/<filename>')
def send_out_image(filename):
	print("sending out_image " + filename)
	return send_from_directory('../out/', filename)

def stream_template(template_name, **context):
	app.update_template_context(context)
	t = app.jinja_env.get_template(template_name)
	rv = t.stream(context)
	return rv

@app.route('/create_image')
def create_image():
	if 'style_im' in session:
		style_im = session['style_im']
		num_iters = session['num_iters']
	else:
		style_im = None
		num_iters = 0
	session.pop('style_im', None)
	session.pop('num_iters', None)
	return Response(stream_template('create_image.html', style_im=style_im, data=make_image.run('./uploads/' + style_im, num_iters)))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))

app.secret_key = '\xbd\x90\xf9\x1e\xd4f/\xde\xef\xc2\x9b\x03\x9a/\x80\x15\xf6\x95\x0c\xf6\xf4\xb0\x10\x0e'