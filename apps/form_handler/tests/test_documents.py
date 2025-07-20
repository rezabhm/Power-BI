from django.test import TestCase
from mongoengine import connect, disconnect
from apps.form_handler.documents import (
    CustomUser,
    FolderType,
    Folder,
    FormStructure,
    FormStructureColumn,
    FormStructureSpecifications,
    Form,
    FormRecord,
    FormRecordCell,
    UploadFile,
)

class DocumentTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        connect('testdb', host='mongomock://localhost')

    @classmethod
    def tearDownClass(cls):
        disconnect()
        super().tearDownClass()

    def setUp(self):
        self.user = CustomUser.objects.create(username='testuser')
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

class CustomUserDocumentTest(DocumentTestCase):
    def test_create_custom_user(self):
        user = CustomUser.objects.create(username='newuser')
        self.assertEqual(user.username, 'newuser')

class FolderTypeDocumentTest(DocumentTestCase):
    def test_create_folder_type(self):
        folder_type = FolderType.objects.create(type_name='new_type')
        self.assertEqual(folder_type.type_name, 'new_type')

class FolderDocumentTest(DocumentTestCase):
    def test_create_folder(self):
        folder = Folder.objects.create(
            name='new_folder',
            folder_owner=self.user,
            folder_type=self.folder_type
        )
        self.assertEqual(folder.name, 'new_folder')

class FormStructureDocumentTest(DocumentTestCase):
    def test_create_form_structure(self):
        form_structure = FormStructure.objects.create(
            structure_name='new_structure',
            folder=self.folder
        )
        self.assertEqual(form_structure.structure_name, 'new_structure')

    def test_add_column_to_form_structure(self):
        column = FormStructureColumn(key_name='key', title='title')
        self.form_structure.columns.append(column)
        self.form_structure.save()
        self.assertEqual(len(self.form_structure.columns), 1)

    def test_add_specification_to_form_structure(self):
        specification = FormStructureSpecifications(name='spec', content='content')
        self.form_structure.specifications.append(specification)
        self.form_structure.save()
        self.assertEqual(len(self.form_structure.specifications), 1)

class FormDocumentTest(DocumentTestCase):
    def test_create_form(self):
        form = Form.objects.create(
            form_structure=self.form_structure,
            user=self.user
        )
        self.assertIsNotNone(form.id)

class FormRecordDocumentTest(DocumentTestCase):
    def test_create_form_record(self):
        form_record = FormRecord.objects.create(
            form=self.form,
            user=self.user
        )
        self.assertIsNotNone(form_record.id)

class FormRecordCellDocumentTest(DocumentTestCase):
    def test_create_form_record_cell(self):
        form_record_cell = FormRecordCell.objects.create(
            form_record=self.form_record,
            form_structure_column=self.form_structure,
            user=self.user,
            content='test_content'
        )
        self.assertEqual(form_record_cell.content, 'test_content')

class UploadFileDocumentTest(DocumentTestCase):
    def test_create_upload_file(self):
        upload_file = UploadFile.objects.create(
            file_name='test_file.txt',
            user=self.user
        )
        self.assertEqual(upload_file.file_name, 'test_file.txt')
