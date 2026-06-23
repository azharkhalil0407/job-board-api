from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employer = User.objects.create_user(
            username='testemployer',
            email='employer@test.com',
            password='testpass123',
            role='employer',
        )
        self.candidate = User.objects.create_user(
            username='testcandidate',
            email='candidate@test.com',
            password='testpass123',
            role='candidate',
        )

    def get_token(self, username, password):
        response = self.client.post('/api/accounts/login/', {
            'username': username,
            'password': password,
        }, format='json')
        return response.data['access']

    def test_register_as_employer(self):
        response = self.client.post('/api/accounts/register/', {
            'username': 'newemployer',
            'email': 'new@employer.com',
            'password': 'strongpass123',
            'role': 'employer',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], 'employer')
        self.assertNotIn('password', response.data)

    def test_register_with_invalid_role(self):
        response = self.client.post('/api/accounts/register/', {
            'username': 'badrole',
            'email': 'bad@role.com',
            'password': 'strongpass123',
            'role': 'manager',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_login_returns_tokens(self):
        response = self.client.post('/api/accounts/login/', {
            'username': 'testemployer',
            'password': 'testpass123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        response = self.client.post('/api/accounts/login/', {
            'username': 'testemployer',
            'password': 'wrongpassword',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_requires_authentication(self):
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_user_data(self):
        token = self.get_token('testemployer', 'testpass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/accounts/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testemployer')
        self.assertEqual(response.data['role'], 'employer')
        self.assertNotIn('password', response.data)
