#!/usr/bin/env python
from coverage import coverage
cov = coverage(branch=True, omit=['tests.py'])
cov.start()

import os
import unittest
from unittest.mock import patch, MagicMock

from config import basedir
from app import app, db
from app.models import User, Image

from app.make_image import make_image
import os.path

import oauth

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_user(self):
        u = User(social_id="facebook$123", nickname="Test User")
        db.session.add(u)
        db.session.commit()
        assert u.is_authenticated is True
        assert u.is_active is True
        assert u.is_anonymous is False

    # check that make_image function cleans up all but last temporary image
    def test_make_image_cleanup(self):
        image_generator = make_image('tests/starry_night1.jpg', 5)
        temp_images = []
        for image in image_generator:
            temp_images.append(image)
        for image in temp_images[0:-1]:
            assert not os.path.exists(os.path.join(app.config['INTERMEDIATE_IM_DIR'], image))

    def test_facebook_oath_authorize(self):
        rv = self.app.get('/authorize/facebook')
        # response should be a redirect
        assert rv.status_code == 302
        # should redirect to facebook's authorization endpoint
        assert rv.location.split('?')[0] == 'https://graph.facebook.com/oauth/authorize'

    
    # we mock out the entire callback method because it depends on request.args
    # coming from an external client (Facebook)
    @patch.object(oauth.FacebookSignIn, 'callback')
    def test_facebook_oath_callback(self, mock_callback):
        mock_callback.return_value = 'facebook$id1', 'Andrea'
        rv = self.app.get('/callback/facebook')
        # when response is new user, db entry created
        assert db.session.query(User).count() == 1
        # when response is existing user, no entry added
        mock_callback.return_value = 'facebook$id1', 'Andy'
        self.app = app.test_client()
        rv = self.app.get('/callback/facebook')
        assert User.query.filter_by(social_id='facebook$id1').count() == 1
        # if user's nickname has changed, db entry is updated
        user = User.query.filter_by(social_id='facebook$id1').first()
        assert user.nickname == 'Andy'
        # check that user is logged in

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report(show_missing=True)
    print("HTML version: " + os.path.join(basedir, "tests/coverage/index.html"))
    cov.html_report(directory='tests/coverage')
    cov.erase()