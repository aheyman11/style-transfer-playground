#!/usr/bin/env python
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

    # check that make_image function cleans up all but last temporary image
    def test_make_image_cleanup(self):
        image_generator = make_image('tests/starry_night1.jpg', 5)
        temp_images = []
        for image in image_generator:
            temp_images.append(image)
        for image in temp_images[0:-1]:
            assert not os.path.exists(os.path.join(app.config['INTERMEDIATE_IM_DIR'], image))


    # def test_avatar(self):
    #     u = User(nickname='john', email='john@example.com')
    #     avatar = u.avatar(128)
    #     expected = 'http://www.gravatar.com/avatar/d4c74594d841139328695756648b6bd6'
    #     assert avatar[0:len(expected)] == expected

    # def test_make_unique_nickname(self):
    #     u = User(nickname='john', email='john@example.com')
    #     db.session.add(u)
    #     db.session.commit()
    #     nickname = User.make_unique_nickname('john')
    #     assert nickname != 'john'
    #     u = User(nickname=nickname, email='susan@example.com')
    #     db.session.add(u)
    #     db.session.commit()
    #     nickname2 = User.make_unique_nickname('john')
    #     assert nickname2 != 'john'
    #     assert nickname2 != nickname

if __name__ == '__main__':
    unittest.main()