import json
import unittest

from app import db, create_app
from app.models import User
from tests.conftest import TestConfig, get_headers


class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test client
        self.client = self.app.test_client()

        # Create test users
        self.u1 = User(username='alice', email='alice@example.com')
        self.u1.set_password('password')
        self.u2 = User(username='bob', email='bob@example.com')
        self.u2.set_password('password')

        db.session.add(self.u1)
        db.session.add(self.u2)
        db.session.commit()

        # Get auth token for u1
        self.token1 = self.u1.get_token()
        db.session.commit()


    def test_get_user_success(self):
        response = self.client.get(
            f'/api/users/{self.u1.id}',
            headers=get_headers(self.token1)
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(data['id'], self.u1.id)

    def test_get_user_unauthorized(self):
        response = self.client.get(f'/api/users/{self.u1.id}')

        self.assertEqual(response.status_code, 401)

    def test_get_user_not_found(self):
        response = self.client.get(
            f'/api/users/9999',
            headers=get_headers(self.token1)
        )

        self.assertEqual(response.status_code, 404)

    def test_get_users(self):
        response = self.client.get(
            f'/api/users',
            headers=get_headers(self.token1)
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(len(data['items']), 2)

    def test_get_users_unauthorized(self):
        response = self.client.get(f'/api/users')

        self.assertEqual(response.status_code, 401)

    def test_get_followers(self):
        self.u2.follow(self.u1)
        db.session.commit()

        response = self.client.get(
            f'/api/users/{self.u1.id}/followers',
            headers=get_headers(self.token1)
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['username'], self.u2.username)

    def test_get_followers_unauthorized(self):
        response = self.client.get(f'/api/users/{self.u1.id}/followers')

        self.assertEqual(response.status_code, 401)

    def test_get_following(self):
        self.u1.follow(self.u2)
        db.session.commit()

        response = self.client.get(
            f'/api/users/{self.u1.id}/following',
            headers=get_headers(self.token1)
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['username'], self.u2.username)

    def test_get_following_unauthorized(self):
        response = self.client.get(f'/api/users/{self.u1.id}/following')

        self.assertEqual(response.status_code, 401)

    def test_create_user_success(self):
        user_data = {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': 'password123'
        }

        response = self.client.post(
            '/api/users',
            data=json.dumps(user_data),
            headers=get_headers()
        )

        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)

        self.assertEqual(data['username'], 'charlie')
        self.assertIn('Location', response.headers)

        # Verify user was created in database
        user = User.query.filter_by(username='charlie').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password123'))

    def test_create_user_missing_data(self):
        user_data = {
            'username': 'charlie',
            'email': 'charlie@example.com'
        }

        response = self.client.post(
            '/api/users',
            data=json.dumps(user_data),
            headers=get_headers()
        )

        self.assertEqual(response.status_code, 400)

    def test_create_user_duplicate_username(self):
        user_data = {
            'username': 'alice',
            'email': 'charlie@example.com',
            'password': 'password123'
        }

        response = self.client.post(
            '/api/users',
            data=json.dumps(user_data),
            headers=get_headers()
        )

        self.assertEqual(response.status_code, 400)

    def test_create_user_duplicate_email(self):
        user_data = {
            'username': 'charlie',
            'email': 'alice@example.com',
            'password': 'password123'
        }

        response = self.client.post(
            '/api/users',
            data=json.dumps(user_data),
            headers=get_headers()
        )

        self.assertEqual(response.status_code, 400)

    def test_update_user_success(self):
        user_data = {
            'username': 'charlie',
            'email': 'alice@example.com',
            'password': 'password123'
        }

        response = self.client.put(
            f'/api/users/{self.u1.id}',
            data=json.dumps(user_data),
            headers=get_headers(self.token1)
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        print(data)
        self.assertEqual(data['username'], 'charlie')

    def test_update_user_unauthorized(self):
        user_data = {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': 'password123'
        }

        response = self.client.put(
            f'/api/users/{self.u1.id}',
            data=json.dumps(user_data),
            headers=get_headers()
        )

        self.assertEqual(response.status_code, 401)

    def test_update_user_wrong_token(self):
        user_data = {
            'username': 'charlie',
            'email': 'charlie@example.com',
            'password': 'password123'
        }

        response = self.client.put(
            f'/api/users/9999',
            data=json.dumps(user_data),
            headers=get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 403)

    def test_update_user_invalid_username(self):
        user_data = {
            'username': 'bob',
            'email': 'charlie@example.com',
            'password': 'password123'
        }
        response = self.client.put(
            f'/api/users/{self.u1.id}',
            data=json.dumps(user_data),
            headers=get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'please use a different username')

    def test_update_user_invalid_email(self):
        user_data = {
            'username': 'alice',
            'email': 'bob@example.com',
            'password': 'password123'
        }
        response = self.client.put(
            f'/api/users/{self.u1.id}',
            data=json.dumps(user_data),
            headers=get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'please use a different email address')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
