from django.test import TestCase
from django.contrib.auth.models import User
from apps.core.serializers import UserSerializer

class UserSerializerTest(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'email': 'test@example.com'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_serializer_valid_data(self):
        """
        Test UserSerializer with valid data.
        """
        serializer = UserSerializer(instance=self.user)
        data = serializer.data
        self.assertEqual(data['username'], self.user_data['username'])
        self.assertEqual(data['email'], self.user_data['email'])

    def test_user_serializer_create_user(self):
        """
        Test UserSerializer for creating a new user.
        """
        new_user_data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'new@example.com'
        }
        serializer = UserSerializer(data=new_user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, new_user_data['username'])
        self.assertEqual(user.email, new_user_data['email'])

    def test_user_serializer_update_user(self):
        """
        Test UserSerializer for updating an existing user.
        """
        updated_data = {
            'username': 'updateduser',
            'email': 'updated@example.com'
        }
        serializer = UserSerializer(instance=self.user, data=updated_data, partial=True)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, updated_data['username'])
        self.assertEqual(user.email, updated_data['email'])
