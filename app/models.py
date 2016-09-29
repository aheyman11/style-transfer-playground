from app import db
from flask.ext.login import UserMixin

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(64), nullable=False, unique=True)
	nickname = db.Column(db.String(64), nullable=False)
	images = db.relationship('Image', backref='author', lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.name)

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
	filepath = db.Column(db.String(64), index=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Image %r>' % (self.filepath)

	@staticmethod
	def make_unique_filename(filename):
		if Image.query.filter_by(filename=filename).first() is None:
			return filename
		version = 2
		while True:
			new_filename = filename + str(version)
			if Image.query.filter_by(filename=new_filename).first() is None:
				break
			version += 1
		return new_filename