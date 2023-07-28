import unittest
from flask import json
from .. import create_app
from ..config.config import config_dict
from ..utils import db
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from ..models.users import User

class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=config_dict['test'])

        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()

    def tearDown(self):
        db.drop_all()

        self.appctx.pop()

        self.app = None

        self.client =None


    def test_user_registration(self):

        signup_data = {
            "username": "testuser",
            "email": "testuser@test.com", 
            "password": "test"
        }

        response = self.client.post('/auth/signup', json=signup_data)

        self.assertEqual(response.status_code, 201)

        response_data = json.loads(response.data)
        self.assertEqual(response_data['username'], 'testuser')
        self.assertEqual(response_data['email'], 'testuser@test.com')

    
    def test_user_login(self):
        login_data = {
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/login', json=login_data)

        # assert response.status_code == 200
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(login_data['email'], 'testuser@gmail.com')

    
    def test_refresh_endpoint(self):
    
        # Create a mock refresh token
        refresh_token = create_access_token(identity='testuser@test.com')

        # Set the authorization header with the refresh token
        headers = {
            'Authorization': f'Bearer {refresh_token}'
        }

        # Send a POST request to the refresh endpoint
        response = self.client.post('/auth/refresh', headers=headers)

        # Print the response data and content
        print(response.data)
        print(response.get_data(as_text=True))

        # Assert the response data
        response_data = json.loads(response.data)
        assert response_data['msg'] == 'Only refresh tokens are allowed'