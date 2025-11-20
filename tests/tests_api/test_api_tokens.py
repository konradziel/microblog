import unittest
import json
from base64 import b64encode

from app import db, create_app
from app.models import User
from config import TestConfig

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.u1 = User(username='alice', email='alice@example.com')
        self.u1.set_password('cat')
        db.session.add(self.u1)
        db.session.commit()
        self.client = self.app.test_client()
        self.token1 = self.u1.get_token()
        db.session.commit()

    @staticmethod
    def get_headers(token=None):
        """Method to get authentication headers."""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        return headers
    
    @staticmethod
    def get_basic_auth_headers(username, password):
        """Method to get basic authentication headers."""
        credentials = b64encode(f'{username}:{password}'.encode()).decode('utf-8')
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {credentials}'
        }

    def test_get_token_success(self):
        response = self.client.post(
            '/api/tokens',
            headers=self.get_basic_auth_headers('alice', 'cat')
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('token', data)
        self.assertTrue(isinstance(data['token'], str))
        self.assertTrue(len(data['token']) > 0)

    def test_get_token_invalid_credentials(self):
        response = self.client.post(
            '/api/tokens',
            headers=self.get_basic_auth_headers('alice', 'dog')
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Unauthorized')
        
    def test_get_token_missing_auth(self):
        response = self.client.post(
            '/api/tokens',
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Unauthorized')
        
    def test_revoke_token_success(self):
        response = self.client.delete(
            '/api/tokens',
            headers=self.get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b'')
        
    def test_revoke_token_unauthorized(self):
        response = self.client.delete('/api/tokens')
        self.assertEqual(response.status_code, 401)

    def test_use_revoked_token(self):
        response = self.client.get(
            f'/api/users/{self.u1.id}',
            headers=self.get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['username'], 'alice')
        
        response = self.client.delete(
            '/api/tokens',
            headers=self.get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 204)
        
        response = self.client.get(
            f'/api/users/{self.u1.id}',
            headers=self.get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Unauthorized')

    def test_update_user_unauthorized(self):
        response = self.client.put(
            f'/api/users/9999',
            headers=self.get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 403)

    def test_update_user_invalid_username(self):
        response = self.client.put(
            f'/api/users/{self.u1.id}',
            headers=self.get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid username')

    def test_update_user_invalid_email(self):
        response = self.client.put(
            f'/api/users/{self.u1.id}',
            headers=self.get_headers(self.token1)
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Invalid email')
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
