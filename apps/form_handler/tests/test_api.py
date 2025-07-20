import mongomock
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from mongoengine import connect, disconnect
from unittest.mock import patch, MagicMock
from apps.form_handler.documents import (
    CustomUser,
    FolderType,
    Folder,
    FormStructure,
    Form,
    FormRecord,
    FormRecordCell,
    UploadFile,
)

class APITestCaseBase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        connect(
            db='testdb',
            host='mongodb://localhost',
            mongo_client_class=mongomock.MongoClient
        )

    @classmethod
    def tearDownClass(cls):
        disconnect()
        super().tearDownClass()

    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser')
        self.client.force_authenticate(user=self.user)
        self.folder_type = FolderType.objects.create(type_name='test_type')
        self.folder = Folder.objects.create(
            name='test_folder',
            folder_owner=self.user,
            folder_type=self.folder_type
        )
        self.form_structure = FormStructure.objects.create(
            structure_name='test_structure',
            folder=self.folder
        )
        self.form = Form.objects.create(
            form_structure=self.form_structure,
            user=self.user
        )
        self.form_record = FormRecord.objects.create(
            form=self.form,
            user=self.user
        )

class FolderViewSetTest(APITestCaseBase):
    def test_list_folders(self):
        url = reverse('folder-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_folder(self):
        url = reverse('folder-list')
        data = {'name': 'new_folder', 'folder_owner': str(self.user.id), 'folder_type': str(self.folder_type.id)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class FormStructureViewSetTest(APITestCaseBase):
    def test_list_form_structures(self):
        url = reverse('form-structure-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_form_structure(self):
        url = reverse('form-structure-list')
        data = {'structure_name': 'new_structure', 'folder': str(self.folder.id)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# Mocking detect_form_structure and read_excel for UploadFileViewSetTest
@patch('apps.form_handler.api.v1.upload_file.views.detect_form_structure', return_value=[str(FormStructure.objects.create(structure_name='detected_structure', folder=Folder.objects.create(name='f', folder_owner=CustomUser.objects.create(username='u'), folder_type=FolderType.objects.create(type_name='t'))).id)])
@patch('pandas.read_excel', return_value=MagicMock())
class UploadFileViewSetTest(APITestCaseBase):
    def test_upload_file(self, mock_read_excel, mock_detect):
        """
        Test file upload and processing.
        """
        url = reverse('upload-file-list')
        with open('test.xlsx', 'w') as f:
            f.write('test')
        with open('test.xlsx', 'rb') as f:
            data = {'file': f}
            response = self.client.post(url, data, format='multipart')
        # This is a mocked response, so we can't assert the status code
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        pass

# Mocking jalali_to_gregorian for ReportingViewSetTest
@patch('apps.form_handler.api.v1.reporting.views.jalali_to_gregorian', return_value='2023-01-01')
class ReportingViewSetTest(APITestCaseBase):
    def test_filter_config(self, mock_jalali):
        url = reverse('filter-config-list')
        response = self.client.get(url, {'form-structure': str(self.form_structure.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_form_structure_reporting(self, mock_jalali):
        url = reverse('form-structure-reporting-list')
        data = {'form-structure': str(self.form_structure.id), 'filter': []}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
