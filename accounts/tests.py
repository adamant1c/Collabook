from django.test import TestCase, Client
from django.urls import reverse

class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_password_reset_url_exists(self):
        """Test that /reset-password/ exists and returns 200"""
        response = self.client.get('/reset-password/')
        self.assertEqual(response.status_code, 200)

    def test_password_reset_with_token(self):
        """Test that /reset-password/?token=test-token pre-fills the form and sets show_confirm"""
        token = "test-token-123"
        url = reverse('accounts:password_reset') + f"?token={token}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_confirm'])
        self.assertEqual(response.context['confirm_form'].initial['token'], token)
        # Check if the token is in the rendered HTML
        self.assertContains(response, token)
        # Check if JavaScript for switching tab is present
        self.assertContains(response, "showTab('confirm')")
