import unittest

from app.models import User, Post, Message, Notification, Task
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

        db.session.commit()

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

    def test_following_posts(self):
        self.u1.follow(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        post1 = Post(body='post from bob', author=self.u2)
        db.session.add(post1)
        db.session.commit()

        posts = db.session.scalars(self.u1.following_posts()).all()
        self.assertEqual(len(posts), 1)

    def test_get_reset_password_token(self):
        token = self.u1.get_reset_password_token()
        self.assertIsNotNone(token)

    def test_verify_reset_password_token(self):
        token = self.u1.get_reset_password_token()
        user = User.verify_reset_password_token(token)
        self.assertEqual(user, self.u1)

    def test_unread_messages_count(self):
        self.assertEqual(self.u1.unread_message_count(), 0)
        
        msg = Message(body='test message', author=self.u2, recipient=self.u1)
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(self.u1.unread_message_count(), 1)

    def test_add_notification(self):
        self.u1.add_notification('test', 'test notification')
        db.session.commit()

        notifications = db.session.query(Notification).filter_by(user_id=self.u1.id).all()
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0].name, 'test')
        self.assertEqual(notifications[0].payload_json, '"test notification"')

    def test_posts_count(self):
        self.assertEqual(self.u1.posts_count(), 0)
        post = Post(body='test post', author=self.u1)
        db.session.add(post)
        db.session.commit()
        self.assertEqual(self.u1.posts_count(), 1)

    def test_to_dict(self):
        dictionary = self.u1.to_dict(include_email=True)
        self.assertEqual(dictionary['username'], 'alice')
        self.assertEqual(dictionary['email'], 'alice@example.com')
        self.assertIsNotNone(dictionary['last_seen'])
        self.assertIsNone(dictionary['about_me'])
        self.assertEqual(dictionary['post_count'], 0)
        self.assertEqual(dictionary['follower_count'], 0)
        self.assertEqual(dictionary['following_count'], 0)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()