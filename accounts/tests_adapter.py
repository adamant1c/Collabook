from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from unittest.mock import patch, MagicMock
from accounts.adapters import MyAccountAdapter
from django.urls import reverse

class AdapterTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.adapter = MyAccountAdapter()

    @patch('accounts.adapters.CollabookAPI')
    def test_redirect_to_create_if_no_character(self, mock_api):
        # Setup request
        request = self.factory.get('/accounts/login/callback/')
        request.user = self.user
        
        # Add session
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session['token'] = 'fake_token'
        request.session.save()
        
        # Mock API response: User has NO character (or empty profession)
        mock_api.get_current_user.return_value = {'character': {'profession': None}}
        
        url = self.adapter.get_login_redirect_url(request)
        
        self.assertEqual(url, reverse('character:create'))

    @patch('accounts.adapters.CollabookAPI')
    def test_redirect_to_default_if_has_profession(self, mock_api):
        request = self.factory.get('/accounts/login/callback/')
        request.user = self.user
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session['token'] = 'fake_token'
        request.session.save()

        # Mock API: User HAS profession
        mock_api.get_current_user.return_value = {'character': {'profession': 'Warrior'}}
        
        url = self.adapter.get_login_redirect_url(request)
        
        # Default should contain world selection (from settings.LOGIN_REDIRECT_URL)
        expected = reverse('world:selection')
        self.assertEqual(url, expected)

    @patch('accounts.adapters.CollabookAPI')
    def test_redirect_to_create_if_no_character_object(self, mock_api):
        request = self.factory.get('/accounts/login/callback/')
        request.user = self.user
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session['token'] = 'fake_token'
        request.session.save()

        # Mock API: User has NO character object at all
        mock_api.get_current_user.return_value = {'character': None}
        
        url = self.adapter.get_login_redirect_url(request)
        
        self.assertEqual(url, reverse('character:create'))
