from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.core import mail

class AccountsAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.password_reset_request_url = reverse('password_reset_request')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'testpassword',
            'email': 'test@example.com'
        }

    def test_user_registration(self):
        """
        Ensure we can register a new user.
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_password_reset_request(self):
        """
        Ensure we can request a password reset.
        """
        User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        response = self.client.post(self.password_reset_request_url, {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # In the view, the email is printed to the console, not sent.
        # So we can't check mail.outbox.
        # I will just check the response status code.

    def test_password_reset_confirm(self):
        """
        Ensure we can confirm a password reset.
        """
        user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

        # This is a simplified version. In a real test, you would get the token from the email.
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        password_reset_confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        new_password = {
            'password': 'newpassword',
            'password2': 'newpassword'
        }

        response = self.client.post(password_reset_confirm_url, new_password, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword'))
