from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

class UserAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.list_create_url = reverse('user-list')
        self.detail_url = reverse('user-detail', kwargs={'pk': self.user.pk})

    def test_get_user_list(self):
        """
        Ensure we can get the list of users.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user(self):
        """
        Ensure we can create a new user.
        """
        data = {'username': 'newuser', 'password': 'newpassword'}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_user_detail(self):
        """
        Ensure we can get the detail of a user.
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        """
        Ensure we can update a user.
        """
        data = {'username': 'updateduser'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_user(self):
        """
        Ensure we can delete a user.
        """
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_user_access(self):
        """
        Ensure unauthenticated users cannot access the API.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class JWTAuthTest(APITestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_user_login(self):
        """
        Ensure we can log in and get a token.
        """
        data = {'username': self.username, 'password': self.password}
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_refresh(self):
        """
        Ensure we can refresh a token.
        """
        refresh = RefreshToken.for_user(self.user)
        data = {'refresh': str(refresh)}
        response = self.client.post(self.refresh_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
