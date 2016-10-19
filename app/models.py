from app import db
from flask.ext.login import UserMixin

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(64), nullable=False, unique=True)
	nickname = db.Column(db.String(64), nullable=False)
	images = db.relationship('Image', backref='author', lazy='dynamic')
	gifs = db.relationship('Gif', backref='author', lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.nickname)

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		try:
			return unicode(self.id)  # python 2
		except NameError:
			return str(self.id)  # python 3

class Image(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	timestamp = db.Column(db.DateTime)
	style_im = db.Column(db.String(64))
	content_im = db.Column(db.String(64))
	num_iters = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Image %r>' % (self.id)

class Gif(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Gif %r>' % (self.id)