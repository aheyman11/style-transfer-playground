#!/usr/bin/env python
from coverage import coverage
cov = coverage(branch=True, omit=['tests.py'])
cov.start()

import os
import unittest

from config import basedir
from app import app, db
from app.models import User, Image

from app.make_image import make_image
import os.path


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