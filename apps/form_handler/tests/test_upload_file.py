from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.documents import CustomUser
from apps.form_handler.documents import FormStructure, FormStructureColumn, Folder, FolderType, UploadFile, \
    FormRecordCell, FormRecord, Form
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import io
from mongoengine import connect, disconnect
import logging

logger = logging.getLogger(__name__)

class UploadFileViewsTestCase(TestCase):
    def setUp(self):
        """
        Sets up the test environment with a MongoDB connection, authenticated clients,
        and test data for UploadFileViewSet.
        """
        # Connect to test MongoDB
        connect('test_db', host='mongomock://localhost')

        # Create test users
        self.admin_user = CustomUser.objects.create(
            username='admin',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
        self.regular_user = CustomUser.objects.create(
            username='user',
            email='user@example.com'
        )

        # Create test folder type and folder
        self.folder_type = FolderType.objects.create(type_name='Test Type')
        self.folder = Folder.objects.create(
            name='Test Folder',
            folder_owner=self.regular_user,
            folder_type=self.folder_type
        )

        # Create test form structure
        self.form_structure = FormStructure.objects.create(
            structure_name='Test Structure',
            folder=self.folder,
            columns=[
                FormStructureColumn(key_name='age', title='Age', content_type='int', excel_column_name='Age'),
                FormStructureColumn(key_name='name', title='Name', content_type='str', excel_column_name='Name')
            ]
        )

        # Create sample Excel file for testing
        data = {'Age': [30, 25], 'Name': ['John Doe', 'Jane Smith']}
        df = pd.DataFrame(data)
        self.excel_content = io.BytesIO()
        df.to_excel(self.excel_content, index=False)
        self.excel_content.seek(0)
        self.excel_file = SimpleUploadedFile('test.xlsx', self.excel_content.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Set up API clients
        self.admin_client = APIClient()
        self.user_client = APIClient()
        self.unauthenticated_client = APIClient()

        # Generate JWT tokens
        admin_refresh = RefreshToken.for_user(self.admin_user)
        user_refresh = RefreshToken.for_user(self.regular_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')
        self.user_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_refresh.access_token}')

    def tearDown(self):
        """
        Cleans up the test MongoDB database after each test.
        """
        disconnect()

    def test_upload_file_valid(self):
        """
        Tests successful file upload with a valid Excel file.
        """
        data = {'file': self.excel_file}
        response = self.user_client.post(reverse('upload-file-list'), data, format='multipart')
        logger.debug("Response data: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'File upload completed successfully.')
        self.assertEqual(UploadFile.objects.count(), 1)
        self.assertEqual(Form.objects.count(), 1)
        self.assertEqual(FormRecord.objects.count(), 2)
        self.assertEqual(FormRecordCell.objects.count(), 4)

    def test_upload_file_no_file(self):
        """
        Tests file upload without providing a file.
        """
        response = self.user_client.post(reverse('upload-file-list'), {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'No file provided.')

    def test_upload_file_invalid_excel(self):
        """
        Tests file upload with an invalid Excel file.
        """
        invalid_file = SimpleUploadedFile('invalid.txt', b'not an excel file', content_type='text/plain')
        data = {'file': invalid_file}
        response = self.user_client.post(reverse('upload-file-list'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertTrue(response.data['message'].startswith('Error reading file:'))

    def test_upload_file_duplicate(self):
        """
        Tests uploading a file with a duplicate name.
        """
        UploadFile.objects.create(
            file_name='uploads/test.xlsx',
            user=self.regular_user,
            form_structure=self.form_structure
        )
        self.excel_content.seek(0)
        data = {'file': SimpleUploadedFile('test.xlsx', self.excel_content.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = self.user_client.post(reverse('upload-file-list'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'This file has already been uploaded.')

    def test_list_uploaded_files(self):
        """
        Tests listing uploaded files for the authenticated user.
        """
        UploadFile.objects.create(
            file_name='uploads/test1.xlsx',
            user=self.regular_user,
            form_structure=self.form_structure
        )
        response = self.user_client.get(reverse('upload-file-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['file_name'], 'http://localhost:8000/uploads/test1.xlsx')

    def test_list_uploaded_files_unauthenticated(self):
        """
        Tests listing uploaded files without authentication.
        """
        response = self.unauthenticated_client.get(reverse('upload-file-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_file_admin_access(self):
        """
        Tests file upload by an admin user.
        """
        data = {'file': self.excel_file}
        self.excel_content.seek(0)
        response = self.admin_client.post(reverse('upload-file-list'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UploadFile.objects.count(), 1)
        self.assertEqual(Form.objects.count(), 1)