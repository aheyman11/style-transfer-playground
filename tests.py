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
import flask

from app.make_image import make_image
import os.path
from shutil import copyfile

from werkzeug.datastructures import FileStorage

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        app.config['INTERMEDIATE_IM_DIR'] = os.path.join(basedir, 'tests', 'tmp')
        app.config['UPLOAD_DIR'] = os.path.join(basedir, 'tests', 'uploads')
        app.config['OUT_DIR'] = os.path.join(basedir, 'tests', 'out')
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

    @patch('oauth.OAuth2Service.get_auth_session')
    def test_facebook_oath_callback2(self, mock_get_auth_session):        
        mock_session = MagicMock()
        mock_get_response = MagicMock(status_code=200, json=MagicMock(return_value={'first_name': 'Andrea', 'id': '3617923766551'}))
        mock_session.get.return_value = mock_get_response
        mock_get_auth_session.return_value = mock_session
        rv = self.app.get('/callback/facebook?code=some_code')
        # when response is new user, db entry created
        assert db.session.query(User).count() == 1
        # when response is existing user, no entry added
        mock_get_response.json.return_value = {'first_name': 'Andy', 'id': '3617923766551'}
        self.app = app.test_client() # need to reset test_client when making another request
        rv = self.app.get('/callback/facebook?code=some_code')
        assert User.query.filter_by(social_id='facebook$3617923766551').count() == 1
        # if user's nickname has changed, db entry is updated
        user = User.query.filter_by(social_id='facebook$3617923766551').first()
        assert user.nickname == 'Andy'

    def test_upload_images(self):
        # remove test file from uploads directory if present
        if os.path.exists(os.path.join(app.config['UPLOAD_DIR'], 'tests_starry_night1.jpg')):
            os.remove(os.path.join(app.config['UPLOAD_DIR'], 'tests_starry_night1.jpg'))
        # create FileStorage object from input file
        test_file = None
        with open('tests/starry_night1.jpg', 'rb') as fp:
            test_file = FileStorage(fp)
            # need test_request_context so we can access session
            with app.test_request_context(path='/upload_images', method='POST', data=dict(num_iter='3', style_im=test_file)):
                rv = app.dispatch_request() # need this to actually send request
                # assert session contains the right data
                assert flask.session['num_iters'] == 3
                assert flask.session['style_im'] == 'tests_starry_night1.jpg'
        assert os.path.exists(os.path.join(app.config['UPLOAD_DIR'], 'tests_starry_night1.jpg'))

    def test_create_image(self):
        with app.test_request_context(path='/create_image'):
            flask.session['num_iters'] = 3
            flask.session['style_im'] = 'tests_starry_night1.jpg'
            rv = app.dispatch_request()
        assert rv.status_code == 200

    def test_save_image(self):
        # copy final generated image into right directory
        if not os.path.exists(os.path.join(app.config['INTERMEDIATE_IM_DIR'], '4.png')):
            copyfile('tests/4.png', os.path.join(app.config['INTERMEDIATE_IM_DIR'], '4.png'))
        # create fake user
        user = User(social_id="facebook$123", nickname="Test User")
        db.session.add(user)
        db.session.commit()
        with app.test_request_context(path='/save_image', method='POST', data={'out_image': '4.png'}):
            flask.g.user = user
            app.dispatch_request()
        # assert that image entry has been added to database
        user = User.query.filter_by(social_id="facebook$123").first()
        assert Image.query.filter_by(author=user).count() == 1
        image_id = Image.query.filter_by(author=user).first().id
        # assert that file has been saved in filesystem
        assert os.path.exists(os.path.join(app.config['OUT_DIR'], str(image_id) + '.jpg'))

    # set up work common to both the following tests
    # create two users, user1 and user2
    # create one image whose author is user1
    def delete_image_setup(self):
        # place image in out directory if it's not already there
        if not os.path.exists(os.path.join(app.config['OUT_DIR'], '1.jpg')):
            copyfile('tests/4.png', os.path.join(app.config['OUT_DIR'], '1.jpg'))
        user1 = User(social_id="facebook$1", nickname="user1")
        user2 = User(social_id="facebook$2", nickname="user2")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        user1 = User.query.filter_by(social_id="facebook$1").first()
        image = Image(author=user1)
        db.session.add(image)
        db.session.commit()

    # user1 deletes her own image: should remove from db and filesystem
    def test_delete_image_authorized(self):
        self.delete_image_setup()
        user1 = User.query.filter_by(social_id="facebook$1").first()
        image = Image.query.first()
        with app.test_request_context(path='/delete_image', method='POST', data={'id': image.id}):
            flask.g.user = user1
            rv = app.dispatch_request()
        assert Image.query.filter_by(id=image.id).count() == 0
        assert not os.path.exists(os.path.join(app.config['OUT_DIR'], str(image.id) + '.jpg'))
    
    # user2 deletes user1's image: should do nothing
    def test_delete_image_unauthorized(self):
        self.delete_image_setup()
        user2 = User.query.filter_by(social_id="facebook$2").first()
        image = Image.query.first()
        with app.test_request_context(path='/delete_image', method='POST', data={'id': image.id}):
            flask.g.user = user2
            rv = app.dispatch_request()
        assert Image.query.filter_by(id=image.id).count() == 1
        assert os.path.exists(os.path.join(app.config['OUT_DIR'], str(image.id) + '.jpg'))

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