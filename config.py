WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

OAUTH_CREDENTIALS = {
	'facebook': {
		'id': '145906095867130',
		'secret': 'b51a44d60219221cfefa614812f9ec59'
	},
	'github': {
		'id': 'c1f6cbbef02ca8cd3d47',
		'secret': 'd3ea82b1007072f37d6d027ad6a772fd9af03e57'
	}
}

INTERMEDIATE_IM_DIR = os.path.join(basedir, 'tmp')
UPLOAD_DIR = os.path.join(basedir, 'uploads')