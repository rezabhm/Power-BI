from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.documents import CustomUser
from apps.form_handler.documents import Folder, FolderType, FormStructure, FormStructureColumn, FormStructureSpecifications, Form, FormRecord, FormRecordCell, UploadFile
from django.core.files.uploadedfile import SimpleUploadedFile
import pandas as pd
import io
from mongoengine import connect, disconnect
import logging

logger = logging.getLogger(__name__)


class FormHandlerViewsTestCase(TestCase):
    def setUp(self) -> None:
        """
        Sets up the test environment with a MongoDB connection, authenticated clients,
        and test data for all viewsets.
        """
        connect('test_db', host='mongomock://localhost')

        # Create test users
        self.admin_user = CustomUser.objects.create(
            username='admin', email='admin@example.com', is_staff=True, is_superuser=True
        )
        self.regular_user = CustomUser.objects.create(
            username='user', email='user@example.com'
        )

        # Create test folder type and folder
        self.folder_type = FolderType.objects.create(type_name='Test Type')
        self.folder = Folder.objects.create(
            name='Test Folder', folder_owner=self.regular_user, folder_type=self.folder_type
        )

        # Create test form structure
        self.form_structure = FormStructure.objects.create(
            structure_name='Test Structure',
            folder=self.folder,
            columns=[
                FormStructureColumn(key_name='age', title='Age', content_type='int', excel_column_name='Age'),
                FormStructureColumn(key_name='name', title='Name', content_type='str', excel_column_name='Name')
            ],
            specifications=[
                FormStructureSpecifications(name='Spec1', content='Content1')
            ]
        )

        # Create test form
        self.form = Form.objects.create(
            form_structure=self.form_structure,
            user=self.regular_user,
            form_name='Test Form'
        )

        # Create test form record
        self.form_record = FormRecord.objects.create(
            form=self.form,
            user=self.regular_user
        )

        # Create test form record cells
        self.form_record_cell = FormRecordCell.objects.create(
            form_record=self.form_record,
            form_structure=self.form_structure,
            form_structure_column='age',
            user=self.regular_user,
            content='30'
        )

        # Create test upload file
        self.upload_file = UploadFile.objects.create(
            file_name='uploads/test.xlsx',
            user=self.regular_user,
            form_structure=self.form_structure
        )

        # Create sample Excel file for testing
        data = {'Age': [30, 25], 'Name': ['John Doe', 'Jane Smith']}
        df = pd.DataFrame(data)
        self.excel_content = io.BytesIO()
        df.to_excel(self.excel_content, index=False)
        self.excel_content.seek(0)
        self.excel_file = SimpleUploadedFile(
            'test.xlsx',
            self.excel_content.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Set up API clients
        self.admin_client = APIClient()
        self.user_client = APIClient()
        self.unauthenticated_client = APIClient()

        # Generate JWT tokens
        admin_refresh = RefreshToken.for_user(self.admin_user)
        user_refresh = RefreshToken.for_user(self.regular_user)
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_refresh.access_token}')
        self.user_client.credentials(HTTP_AUTHORIZATION=f'Bearer {user_refresh.access_token}')

    def tearDown(self) -> None:
        """
        Cleans up the test MongoDB database after each test.
        """
        disconnect()

    # Tests for FolderViewSet
    def test_create_folder(self) -> None:
        """
        Tests creating a new folder with valid data.
        """
        data = {
            'name': 'New Folder',
            'folder_owner': str(self.regular_user.id),
            'folder_type': str(self.folder_type.id)
        }
        response = self.user_client.post(reverse('folder-list'), data, format='json')
        logger.debug("Create folder response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Folder.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Folder')

    def test_create_folder_invalid_data(self) -> None:
        """
        Tests creating a folder with invalid data (missing required field).
        """
        data = {'folder_owner': str(self.regular_user.id), 'folder_type': str(self.folder_type.id)}
        response = self.user_client.post(reverse('folder-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_retrieve_folder(self) -> None:
        """
        Tests retrieving an existing folder by ID.
        """
        response = self.user_client.get(reverse('folder-detail', kwargs={'id': str(self.folder.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.folder.id))
        self.assertEqual(response.data['name'], 'Test Folder')

    def test_update_folder(self) -> None:
        """
        Tests updating an existing folder with full data.
        """
        data = {
            'name': 'Updated Folder',
            'folder_owner': str(self.regular_user.id),
            'folder_type': str(self.folder_type.id)
        }
        response = self.user_client.put(reverse('folder-detail', kwargs={'id': str(self.folder.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.folder.refresh_from_db()
        self.assertEqual(self.folder.name, 'Updated Folder')

    def test_partial_update_folder(self) -> None:
        """
        Tests partially updating an existing folder.
        """
        data = {'name': 'Partially Updated Folder'}
        response = self.user_client.patch(reverse('folder-detail', kwargs={'id': str(self.folder.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.folder.refresh_from_db()
        self.assertEqual(self.folder.name, 'Partially Updated Folder')

    def test_delete_folder(self) -> None:
        """
        Tests deleting an existing folder.
        """
        response = self.user_client.delete(reverse('folder-detail', kwargs={'id': str(self.folder.id)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Folder.objects.count(), 0)

    def test_list_folders(self) -> None:
        """
        Tests listing all folders.
        """
        response = self.user_client.get(reverse('folder-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Folder')

    def test_folder_unauthenticated_access(self) -> None:
        """
        Tests accessing folder endpoints without authentication.
        """
        response = self.unauthenticated_client.get(reverse('folder-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for FolderTypeViewSet
    def test_create_folder_type(self) -> None:
        """
        Tests creating a new folder type with valid data.
        """
        data = {'type_name': 'New Type'}
        response = self.admin_client.post(reverse('folder-type-list'), data, format='json')
        logger.debug("Create folder type response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FolderType.objects.count(), 2)
        self.assertEqual(response.data['type_name'], 'New Type')

    def test_create_folder_type_invalid_data(self) -> None:
        """
        Tests creating a folder type with invalid data (missing required field).
        """
        data = {}
        response = self.admin_client.post(reverse('folder-type-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('type_name', response.data)

    def test_update_folder_type(self) -> None:
        """
        Tests updating an existing folder type.
        """
        data = {'type_name': 'Updated Type'}
        response = self.admin_client.put(reverse('folder-type-detail', kwargs={'id': str(self.folder_type.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.folder_type.refresh_from_db()
        self.assertEqual(self.folder_type.type_name, 'Updated Type')

    def test_delete_folder_type(self) -> None:
        """
        Tests deleting an existing folder type.
        """
        response = self.admin_client.delete(reverse('folder-type-detail', kwargs={'id': str(self.folder_type.id)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FolderType.objects.count(), 0)

    def test_list_folder_types(self) -> None:
        """
        Tests listing all folder types.
        """
        response = self.user_client.get(reverse('folder-type-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type_name'], 'Test Type')

    def test_folder_type_unauthenticated_access(self) -> None:
        """
        Tests accessing folder type endpoints without authentication.
        """
        response = self.unauthenticated_client.get(reverse('folder-type-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for FormStructureViewSet
    def test_create_form_structure(self) -> None:
        """
        Tests creating a new form structure with valid data.
        """
        data = {
            'structure_name': 'New Structure',
            'folder': str(self.folder.id),
            'columns': [{'key_name': 'name', 'title': 'Name', 'content_type': 'str'}]
        }
        response = self.user_client.post(reverse('form-structure-list'), data, format='json')
        logger.debug("Create form structure response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FormStructure.objects.count(), 2)
        self.assertEqual(response.data['structure_name'], 'New Structure')

    def test_create_form_structure_invalid_data(self) -> None:
        """
        Tests creating a form structure with invalid data (missing required field).
        """
        data = {'folder': str(self.folder.id)}
        response = self.user_client.post(reverse('form-structure-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('structure_name', response.data)

    def test_retrieve_form_structure(self) -> None:
        """
        Tests retrieving an existing form structure by ID.
        """
        response = self.user_client.get(reverse('form-structure-detail', kwargs={'id': str(self.form_structure.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.form_structure.id))
        self.assertEqual(response.data['structure_name'], 'Test Structure')

    def test_update_form_structure(self) -> None:
        """
        Tests updating an existing form structure with full data.
        """
        data = {
            'structure_name': 'Updated Structure',
            'folder': str(self.folder.id),
            'columns': [{'key_name': 'age', 'title': 'Age', 'content_type': 'int'}]
        }
        response = self.user_client.put(reverse('form-structure-detail', kwargs={'id': str(self.form_structure.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_structure.refresh_from_db()
        self.assertEqual(self.form_structure.structure_name, 'Updated Structure')

    def test_partial_update_form_structure(self) -> None:
        """
        Tests partially updating an existing form structure.
        """
        data = {'structure_name': 'Partially Updated Structure'}
        response = self.user_client.patch(reverse('form-structure-detail', kwargs={'id': str(self.form_structure.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_structure.refresh_from_db()
        self.assertEqual(self.form_structure.structure_name, 'Partially Updated Structure')

    def test_delete_form_structure(self) -> None:
        """
        Tests deleting an existing form structure.
        """
        response = self.user_client.delete(reverse('form-structure-detail', kwargs={'id': str(self.form_structure.id)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FormStructure.objects.count(), 0)

    def test_list_form_structures(self) -> None:
        """
        Tests listing all form structures.
        """
        response = self.user_client.get(reverse('form-structure-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['structure_name'], 'Test Structure')

    def test_list_form_structures_by_folder(self) -> None:
        """
        Tests listing form structures filtered by folder.
        """
        response = self.user_client.get(reverse('form-structure-list', kwargs={'folder_pk': str(self.folder.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['structure_name'], 'Test Structure')

    def test_form_structure_unauthenticated_access(self) -> None:
        """
        Tests accessing form structure endpoints without authentication.
        """
        response = self.unauthenticated_client.get(reverse('form-structure-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for FormStructureColumnViewSet
    def test_create_form_structure_column(self) -> None:
        """
        Tests creating a new form structure column.
        """
        data = {'key_name': 'score', 'title': 'Score', 'content_type': 'float', 'excel_column_name': 'Score'}
        response = self.user_client.post(
            reverse('form-structure-column-list', kwargs={'form_structure_id': str(self.form_structure.id)}),
            data,
            format='json'
        )
        logger.debug("Create form structure column response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.form_structure.refresh_from_db()
        self.assertEqual(len(self.form_structure.columns), 3)
        self.assertEqual(self.form_structure.columns[-1].key_name, 'score')

    def test_create_form_structure_column_invalid_data(self) -> None:
        """
        Tests creating a form structure column with invalid data.
        """
        data = {'title': 'Score', 'content_type': 'float'}
        response = self.user_client.post(
            reverse('form-structure-column-list', kwargs={'form_structure_id': str(self.form_structure.id)}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('key_name', response.data)

    def test_list_form_structure_columns(self) -> None:
        """
        Tests listing columns for a form structure.
        """
        response = self.user_client.get(
            reverse('form-structure-column-list', kwargs={'form_structure_id': str(self.form_structure.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['key_name'], 'age')

    def test_update_form_structure_column(self) -> None:
        """
        Tests updating an existing form structure column.
        """
        data = {'key_name': 'updated_age', 'title': 'Updated Age', 'content_type': 'int'}
        response = self.user_client.put(
            reverse('form-structure-column-detail', kwargs={'form_structure_id': str(self.form_structure.id), 'pk': 0}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_structure.refresh_from_db()
        self.assertEqual(self.form_structure.columns[0].key_name, 'updated_age')

    def test_delete_form_structure_column(self) -> None:
        """
        Tests deleting a form structure column.
        """
        response = self.user_client.delete(
            reverse('form-structure-column-detail', kwargs={'form_structure_id': str(self.form_structure.id), 'pk': 0})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.form_structure.refresh_from_db()
        self.assertEqual(len(self.form_structure.columns), 1)

    def test_form_structure_column_unauthenticated_access(self) -> None:
        """
        Tests accessing form structure column endpoints without authentication.
        """
        response = self.unauthenticated_client.get(
            reverse('form-structure-column-list', kwargs={'form_structure_id': str(self.form_structure.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_form_structure_specification(self) -> None:
        """
        Tests creating a new form structure specification.
        """
        data = {'name': 'Spec2', 'content': 'Content2'}
        response = self.user_client.post(
            reverse('form-structure-specification-list', kwargs={'form_structure_id': str(self.form_structure.id)}),
            data,
            format='json'
        )
        logger.debug("Create form structure specification response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.form_structure.refresh_from_db()
        self.assertEqual(len(self.form_structure.specifications), 2)
        self.assertEqual(self.form_structure.specifications[-1].name, 'Spec2')

    def test_create_form_structure_specification_invalid_data(self) -> None:
        """
        Tests creating a form structure specification with invalid data.
        """
        data = {'content': 'Content2'}
        response = self.user_client.post(
            reverse('form-structure-specification-list', kwargs={'form_structure_id': str(self.form_structure.id)}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_list_form_structure_specifications(self) -> None:
        """
        Tests listing specifications for a form structure.
        """
        response = self.user_client.get(
            reverse('form-structure-specification-list', kwargs={'form_structure_id': str(self.form_structure.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Spec1')

    def test_update_form_structure_specification(self) -> None:
        """
        Tests updating an existing form structure specification.
        """
        data = {'name': 'Updated Spec', 'content': 'Updated Content'}
        response = self.user_client.put(
            reverse('form-structure-specification-detail', kwargs={'form_structure_id': str(self.form_structure.id), 'pk': 0}),
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_structure.refresh_from_db()
        self.assertEqual(self.form_structure.specifications[0].name, 'Updated Spec')

    def test_delete_form_structure_specification(self) -> None:
        """
        Tests deleting a form structure specification.
        """
        response = self.user_client.delete(
            reverse('form-structure-specification-detail', kwargs={'form_structure_id': str(self.form_structure.id), 'pk': 0})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.form_structure.refresh_from_db()
        self.assertEqual(len(self.form_structure.specifications), 0)

    def test_form_structure_specification_unauthenticated_access(self) -> None:
        """
        Tests accessing form structure specification endpoints without authentication.
        """
        response = self.unauthenticated_client.get(
            reverse('form-structure-specification-list', kwargs={'form_structure_id': str(self.form_structure.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for FormViewSet
    def test_create_form(self) -> None:
        """
        Tests creating a new form with valid data.
        """
        data = {
            'form_structure': str(self.form_structure.id),
            'user': str(self.regular_user.id),
            'form_name': 'New Form'
        }
        response = self.user_client.post(reverse('form-list'), data, format='json')
        logger.debug("Create form response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Form.objects.count(), 2)
        self.assertEqual(response.data['form_name'], 'New Form')

    def test_create_form_invalid_data(self) -> None:
        """
        Tests creating a form with invalid data (missing required field).
        """
        data = {'user': str(self.regular_user.id)}
        response = self.user_client.post(reverse('form-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('form_structure', response.data)

    def test_retrieve_form(self) -> None:
        """
        Tests retrieving an existing form by ID.
        """
        response = self.user_client.get(reverse('form-detail', kwargs={'id': str(self.form.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.form.id))
        self.assertEqual(response.data['form_name'], 'Test Form')

    def test_update_form(self) -> None:
        """
        Tests updating an existing form with full data.
        """
        data = {
            'form_structure': str(self.form_structure.id),
            'user': str(self.regular_user.id),
            'form_name': 'Updated Form'
        }
        response = self.user_client.put(reverse('form-detail', kwargs={'id': str(self.form.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form.refresh_from_db()
        self.assertEqual(self.form.form_name, 'Updated Form')

    def test_partial_update_form(self) -> None:
        """
        Tests partially updating an existing form.
        """
        data = {'form_name': 'Partially Updated Form'}
        response = self.user_client.patch(reverse('form-detail', kwargs={'id': str(self.form.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form.refresh_from_db()
        self.assertEqual(self.form.form_name, 'Partially Updated Form')

    def test_delete_form(self) -> None:
        """
        Tests deleting an existing form.
        """
        response = self.user_client.delete(reverse('form-detail', kwargs={'id': str(self.form.id)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Form.objects.count(), 0)

    def test_list_forms(self) -> None:
        """
        Tests listing all forms.
        """
        response = self.user_client.get(reverse('form-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['form_name'], 'Test Form')

    def test_form_unauthenticated_access(self) -> None:
        """
        Tests accessing form endpoints without authentication.
        """
        response = self.unauthenticated_client.get(reverse('form-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for FormRecordViewSet
    def test_create_form_record(self) -> None:
        """
        Tests creating a new form record with valid data.
        """
        data = {
            'form': str(self.form.id),
            'user': str(self.regular_user.id)
        }
        response = self.user_client.post(reverse('form-record-list'), data, format='json')
        logger.debug("Create form record response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FormRecord.objects.count(), 2)

    def test_create_form_record_invalid_data(self) -> None:
        """
        Tests creating a form record with invalid data (missing required field).
        """
        data = {'user': str(self.regular_user.id)}
        response = self.user_client.post(reverse('form-record-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('form', response.data)

    def test_retrieve_form_record(self) -> None:
        """
        Tests retrieving an existing form record by ID.
        """
        response = self.user_client.get(reverse('form-record-detail', kwargs={'id': str(self.form_record.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.form_record.id))

    def test_update_form_record(self) -> None:
        """
        Tests updating an existing form record with full data.
        """
        data = {
            'form': str(self.form.id),
            'user': str(self.regular_user.id)
        }
        response = self.user_client.put(reverse('form-record-detail', kwargs={'id': str(self.form_record.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_record.refresh_from_db()
        self.assertEqual(self.form_record.form.id, self.form.id)

    def test_partial_update_form_record(self) -> None:
        """
        Tests partially updating an existing form record.
        """
        data = {'user': str(self.admin_user.id)}
        response = self.user_client.patch(reverse('form-record-detail', kwargs={'id': str(self.form_record.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_record.refresh_from_db()
        self.assertEqual(self.form_record.user.id, self.admin_user.id)

    def test_delete_form_record(self) -> None:
        """
        Tests deleting an existing form record.
        """
        response = self.user_client.delete(reverse('form-record-detail', kwargs={'id': str(self.form_record.id)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FormRecord.objects.count(), 0)

    def test_list_form_records(self) -> None:
        """
        Tests listing all form records.
        """
        response = self.user_client.get(reverse('form-record-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_form_record_unauthenticated_access(self) -> None:
        """
        Tests accessing form record endpoints without authentication.
        """
        response = self.unauthenticated_client.get(reverse('form-record-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for FormRecordCellViewSet
    def test_create_form_record_cell(self) -> None:
        """
        Tests creating a new form record cell with valid data.
        """
        data = {
            'form_record': str(self.form_record.id),
            'form_structure_column': 'name',
            'user': str(self.regular_user.id),
            'content': 'Jane Smith'
        }
        response = self.user_client.post(reverse('form-record-cell-list'), data, format='json')
        logger.debug("Create form record cell response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FormRecordCell.objects.count(), 2)
        self.assertEqual(response.data['content'], 'Jane Smith')

    def test_create_form_record_cell_invalid_data(self) -> None:
        """
        Tests creating a form record cell with invalid data (missing required field).
        """
        data = {'form_record': str(self.form_record.id), 'user': str(self.regular_user.id)}
        response = self.user_client.post(reverse('form-record-cell-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('form_structure_column', response.data)

    def test_retrieve_form_record_cell(self) -> None:
        """
        Tests retrieving an existing form record cell by ID.
        """
        response = self.user_client.get(reverse('form-record-cell-detail', kwargs={'id': str(self.form_record_cell.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.form_record_cell.id))
        self.assertEqual(response.data['content'], '30')

    def test_update_form_record_cell(self) -> None:
        """
        Tests updating an existing form record cell with full data.
        """
        data = {
            'form_record': str(self.form_record.id),
            'form_structure_column': 'age',
            'user': str(self.regular_user.id),
            'content': '35'
        }
        response = self.user_client.put(reverse('form-record-cell-detail', kwargs={'id': str(self.form_record_cell.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_record_cell.refresh_from_db()
        self.assertEqual(self.form_record_cell.content, '35')

    def test_partial_update_form_record_cell(self) -> None:
        """
        Tests partially updating an existing form record cell.
        """
        data = {'content': '40'}
        response = self.user_client.patch(reverse('form-record-cell-detail', kwargs={'id': str(self.form_record_cell.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.form_record_cell.refresh_from_db()
        self.assertEqual(self.form_record_cell.content, '40')

    def test_delete_form_record_cell(self) -> None:
        """
        Tests deleting an existing form record cell.
        """
        response = self.user_client.delete(reverse('form-record-cell-detail', kwargs={'id': str(self.form_record_cell.id)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(FormRecordCell.objects.count(), 0)

    def test_list_form_record_cells(self) -> None:
        """
        Tests listing all form record cells.
        """
        response = self.user_client.get(reverse('form-record-cell-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], '30')

    def test_form_record_cell_unauthenticated_access(self) -> None:
        """
        Tests accessing form record cell endpoints without authentication.
        """
        response = self.unauthenticated_client.get(reverse('form-record-cell-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Tests for UploadFileViewSet
    def test_create_upload_file(self) -> None:
        """
        Tests creating a new upload file with valid data.
        """
        data = {'file': self.excel_file, 'user': str(self.regular_user.id), 'form_structure': str(self.form_structure.id)}
        self.excel_content.seek(0)
        response = self.user_client.post(reverse('upload-file-list'), data, format='multipart')
        logger.debug("Create upload file response: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UploadFile.objects.count(), 2)

    def test_create_upload_file_invalid_data(self) -> None:
        """
        Tests creating an upload file with invalid data (missing file).
        """
        data = {'user': str(self.regular_user.id)}
        response = self.user_client.post(reverse('upload-file-list'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file_name', response.data)

    def test_retrieve_upload_file(self) -> None:
        """
        Tests retrieving an existing upload file by ID.
        """
        response = self.user_client.get(reverse('upload-file-detail', kwargs={'id': str(self.upload_file.id)}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.upload_file.id))
        self.assertEqual(response.data['file_name'], 'http://localhost:8000/uploads/test.xlsx')

    def test_update_upload_file(self) -> None:
        """
        Tests updating an existing upload file with full data.
        """
        self.excel_content.seek(0)
        data = {
            'file': SimpleUploadedFile('new_test.xlsx', self.excel_content.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            'user': str(self.regular_user.id),
            'form_structure': str(self.form_structure.id)
        }
        response = self.user_client.put(reverse('upload-file-detail', kwargs={'id': str(self.upload_file.id)}), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.upload_file.refresh_from_db()
        self.assertTrue(self.upload_file.file_name.endswith('new_test.xlsx'))

    def test_partial_update_upload_file(self) -> None:
        """
        Tests partially updating an existing upload file.
        """
        data = {'form_structure': str(self.form_structure.id)}
        response = self.user_client.patch(reverse('upload-file-detail', kwargs={'id': str(self.upload_file.id)}), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.upload_file.refresh_from_db()
        self.assertEqual(self.upload_file.form_structure.id, self.form_structure.id)

    def test_delete_upload_file(self) -> None:
        """
        Tests deleting an existing upload file.
        """
        response = self.user_client.delete(reverse('upload-file-detail', kwargs={'id': str(self.upload_file.id)}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UploadFile.objects.count(), 0)

    def test_list_upload_files(self) -> None:
        """
        Tests listing all upload files.
        """
        response = self.user_client.get(reverse('upload-file-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['file_name'], 'http://localhost:8000/uploads/test.xlsx')

    def test_upload_file_unauthenticated_access(self) -> None:
        """
        Tests accessing upload file endpoints without authentication.
        """
        response = self.unauthenticated_client.get(reverse('upload-file-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)