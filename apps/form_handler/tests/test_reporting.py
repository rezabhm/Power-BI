from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.documents import CustomUser
from apps.form_handler.documents import FormStructure, FormStructureColumn, FormRecordCell, FormRecord, Form
from mongoengine import connect, disconnect
import logging

logger = logging.getLogger(__name__)

class FilterConfigViewsTestCase(TestCase):
    def setUp(self):
        """
        Sets up the test environment with a MongoDB connection, authenticated clients,
        and test data for FilterConfigViewSet.
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

        # Create test form structure with columns
        self.form_structure = FormStructure.objects.create(
            structure_name='Test Structure',
            folder=None,  # Assuming folder can be null for testing
            columns=[
                FormStructureColumn(key_name='age', title='Age', content_type='int', excel_column_name='Age'),
                FormStructureColumn(key_name='name', title='Name', content_type='str', excel_column_name='Name'),
                FormStructureColumn(key_name='score', title='Score', content_type='float', excel_column_name='Score')
            ]
        )

        # Create test form record cell for string content
        FormRecordCell.objects.create(
            form_structure=self.form_structure,
            form_structure_column='name',
            user=self.regular_user,
            content='John Doe'
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

    def tearDown(self):
        """
        Cleans up the test MongoDB database after each test.
        """
        disconnect()

    def test_list_filter_config_valid_form_structure(self):
        """
        Tests successful retrieval of filter configuration for a valid form structure.
        """
        url = reverse('filter-config-list') + f'?form-structure={self.form_structure.id}'
        response = self.user_client.get(url)
        logger.debug("Response data: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('filter-config', response.data)
        self.assertEqual(len(response.data['filter-config']), 5)  # 2 for int, 1 for str, 2 for float
        self.assertTrue(any(config['type'] == 'int' and config['key_name'] == 'age' for config in response.data['filter-config']))
        self.assertTrue(any(config['type'] == 'str' and config['key_name'] == 'name' for config in response.data['filter-config']))
        self.assertTrue(any(config['type'] == 'float' and config['key_name'] == 'score' for config in response.data['filter-config']))

    def test_list_filter_config_invalid_form_structure(self):
        """
        Tests retrieval of filter configuration with an invalid form structure ID.
        """
        url = reverse('filter-config-list') + '?form-structure=invalid_id'
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Invalid form structure ID provided.')

    def test_list_filter_config_unauthenticated(self):
        """
        Tests access to filter config endpoint without authentication.
        """
        url = reverse('filter-config-list') + f'?form-structure={self.form_structure.id}'
        response = self.unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_filter_config_admin_access(self):
        """
        Tests filter config retrieval by an admin user.
        """
        url = reverse('filter-config-list') + f'?form-structure={self.form_structure.id}'
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('filter-config', response.data)
        self.assertEqual(len(response.data['filter-config']), 5)



class FormStructureReportingViewsTestCase(TestCase):
    def setUp(self):
        """
        Sets up the test environment with a MongoDB connection, authenticated clients,
        and test data for FormStructureReportingViewSet.
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

        # Create test form structure
        self.form_structure = FormStructure.objects.create(
            structure_name='Test Structure',
            folder=None,
            columns=[
                FormStructureColumn(key_name='age', title='Age', content_type='int', excel_column_name='Age'),
                FormStructureColumn(key_name='name', title='Name', content_type='str', excel_column_name='Name')
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
        FormRecordCell.objects.create(
            form_record=self.form_record,
            form_structure=self.form_structure,
            form_structure_column='age',
            user=self.regular_user,
            content='30'
        )
        FormRecordCell.objects.create(
            form_record=self.form_record,
            form_structure=self.form_structure,
            form_structure_column='name',
            user=self.regular_user,
            content='John Doe'
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

    def tearDown(self):
        """
        Cleans up the test MongoDB database after each test.
        """
        disconnect()

    def test_create_report_valid_data(self):
        """
        Tests successful report generation with valid filters and date range.
        """
        data = {
            'form-structure': str(self.form_structure.id),
            'filter': [
                {'type': 'int', 'key_name': 'age', 'condition_type': 'gte', 'condition_int': 20},
                {'type': 'str', 'key_name': 'name', 'condition_str_list': ['John Doe']}
            ],
            'data-from': '1403/01/01',
            'data-to': '1404/12/30'
        }
        response = self.user_client.post(reverse('form-structure-reporting-list'), data, format='json')
        logger.debug("Response data: %s", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('form-data', response.data)
        self.assertIn('form-structure-data', response.data)
        self.assertEqual(len(response.data['form-data']), 1)
        self.assertEqual(response.data['form-data'][0]['form_name'], 'Test Form')

    def test_create_report_invalid_form_structure(self):
        """
        Tests report generation with an invalid form structure ID.
        """
        data = {
            'form-structure': 'invalid_id',
            'filter': [
                {'type': 'int', 'key_name': 'age', 'condition_type': 'gte', 'condition_int': 20}
            ]
        }
        response = self.user_client.post(reverse('form-structure-reporting-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Invalid form structure ID provided.')

    def test_create_report_missing_filter(self):
        """
        Tests report generation without providing a filter list.
        """
        data = {'form-structure': str(self.form_structure.id)}
        response = self.user_client.post(reverse('form-structure-reporting-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Filter list is required.')

    def test_create_report_invalid_date_format(self):
        """
        Tests report generation with an invalid date format.
        """
        data = {
            'form-structure': str(self.form_structure.id),
            'filter': [{'type': 'int', 'key_name': 'age', 'condition_type': 'gte', 'condition_int': 20}],
            'data-from': 'invalid_date'
        }
        response = self.user_client.post(reverse('form-structure-reporting-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Invalid start date format.')

    def test_create_report_unauthenticated(self):
        """
        Tests report generation without authentication.
        """
        data = {
            'form-structure': str(self.form_structure.id),
            'filter': [{'type': 'int', 'key_name': 'age', 'condition_type': 'gte', 'condition_int': 20}]
        }
        response = self.unauthenticated_client.post(reverse('form-structure-reporting-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_report_admin_access(self):
        """
        Tests report generation by an admin user.
        """
        data = {
            'form-structure': str(self.form_structure.id),
            'filter': [{'type': 'str', 'key_name': 'name', 'condition_str_list': ['John Doe']}]
        }
        response = self.admin_client.post(reverse('form-structure-reporting-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('form-data', response.data)
        self.assertEqual(len(response.data['form-data']), 1)