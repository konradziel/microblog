import unittest

from app.models import User
from app import db, create_app
from config import TestConfig


class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.u1 = User(username='alice', email='alice@example.com')
        self.u2 = User(username='bob', email='bob@example.com')

        db.session.add(self.u1)
        db.session.add(self.u2)

    def test_init(self):
        u = User()
        self.assertIsInstance(u, User)

    def test_user_repr(self):
        expected_repr = f'<User {self.u1.username}>'
        self.assertEqual(repr(self.u1), expected_repr)
        self.assertEqual(str(self.u1), expected_repr)

    def test_password(self):
        u = User()
        u.set_password('cat')
        self.assertTrue(u.check_password('cat'))
        self.assertFalse(u.check_password('dog'))

    def test_is_following_not_following(self):
        self.assertFalse(self.u1.is_following(self.u2))

    def test_is_following_correct(self):
        self.assertFalse(self.u1.is_following(self.u2))

        self.u1.follow(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))

    def test_unfollow(self):
        self.u1.follow(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))

        self.u1.unfollow(self.u2)
        db.session.commit()

        self.assertFalse(self.u1.is_following(self.u2))

    def test_followers_count(self):
        self.assertEqual(self.u2.followers_count(), 0)

        self.u1.follow(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))

        self.assertEqual(self.u2.followers_count(), 1)

    def test_following_count(self):
        self.assertEqual(self.u1.following_count(), 0)

        self.u1.follow(self.u2)
        db.session.commit()
        self.assertTrue(self.u1.is_following(self.u2))

        self.assertEqual(self.u1.following_count(), 1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()