from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange

class CreateImageForm(Form):
	style_im = FileField('Your style image', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'png'], 'Images only (jpg or png)!')
	])
	content_im = FileField('Your content image', validators=[
		FileRequired(),
		FileAllowed(['jpg', 'png'], 'Images only (jpg or png)!')
	])
	num_iter = IntegerField('num_iter', validators=[
		DataRequired('This must be an integer'),
		NumberRange(min=0, message='Number must be positive')
	])