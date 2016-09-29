from flask import render_template, flash, redirect, url_for, session, send_from_directory, send_file, Response
from werkzeug.utils import secure_filename
from app import app
from .forms import CreateImageForm

import numpy as np
import scipy.misc
from PIL import Image
import time
from io import BytesIO
import base64

import make_image

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/upload_images', methods=('GET', 'POST'))
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

app.secret_key = '\xbd\x90\xf9\x1e\xd4f/\xde\xef\xc2\x9b\x03\x9a/\x80\x15\xf6\x95\x0c\xf6\xf4\xb0\x10\x0e'