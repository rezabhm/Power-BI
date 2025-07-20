import mongoengine as me
import mongomock
from django.test import TestCase
from datetime import datetime
from apps.form_handler.documents import (
    CustomUser, FolderType, Folder, FormStructure, FormStructureColumn,
    FormStructureSpecifications, Form, FormRecord, FormRecordCell, UploadFile
)
import uuid

def random_user_data():
    unique_str = str(uuid.uuid4())[:8]
    return {
        "username": f"user_{unique_str}",
        "email": f"user_{unique_str}@example.com"
    }

class CustomUserTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        data = random_user_data()
        self.user = CustomUser.objects.create(
            username=data["username"],
            email=data["email"],
            is_active=True,
            is_staff=False,
            is_superuser=False,
            roles=["user"]
        )

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_user_creation(self):
        self.assertEqual(self.user.username, self.user.username)
        self.assertEqual(self.user.email, self.user.email)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertEqual(self.user.roles, ["user"])
        self.assertTrue(isinstance(self.user.date_joined, datetime))
        self.assertEqual(str(self.user), self.user.username)

    def test_username_required(self):
        with self.assertRaises(me.errors.ValidationError):
            CustomUser.objects.create(email="no_username@example.com")

    def test_email_optional(self):
        data = random_user_data()
        user = CustomUser.objects.create(username=data["username"])
        self.assertIsNone(user.email)

    def test_unique_username(self):
        data = random_user_data()
        CustomUser.objects.create(username=data["username"], email=data["email"])
        with self.assertRaises(me.errors.NotUniqueError):
            CustomUser.objects.create(username=data["username"], email="another@example.com")

    def test_unique_email(self):
        data = random_user_data()
        CustomUser.objects.create(username=data["username"], email=data["email"])
        with self.assertRaises(me.errors.NotUniqueError):
            CustomUser.objects.create(username="anotheruser", email=data["email"])

class FolderTypeTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        self.folder_type = FolderType.objects.create(type_name="Personal")

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_folder_type_creation(self):
        self.assertEqual(self.folder_type.type_name, "Personal")
        self.assertEqual(str(self.folder_type), "Personal")

    def test_type_name_required(self):
        with self.assertRaises(me.errors.ValidationError):
            FolderType.objects.create()

    def test_type_name_max_length(self):
        with self.assertRaises(me.errors.ValidationError):
            FolderType.objects.create(type_name="A" * 51)

class FolderTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        data = random_user_data()
        self.user = CustomUser.objects.create(username=data["username"], email=data["email"])
        self.folder_type = FolderType.objects.create(type_name="Personal")
        self.folder = Folder.objects.create(
            name="MyFolder",
            folder_owner=self.user,
            folder_type=self.folder_type
        )

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_folder_creation(self):
        self.assertEqual(self.folder.name, "MyFolder")
        self.assertEqual(self.folder.folder_owner, self.user)
        self.assertEqual(self.folder.folder_type, self.folder_type)
        self.assertTrue(isinstance(self.folder.create_date, datetime))
        self.assertEqual(str(self.folder), "MyFolder")

    def test_required_fields(self):
        with self.assertRaises(me.errors.ValidationError):
            Folder.objects.create(name="NoOwnerNoType")
        with self.assertRaises(me.errors.ValidationError):
            Folder.objects.create(folder_owner=self.user)
        with self.assertRaises(me.errors.ValidationError):
            Folder.objects.create(folder_type=self.folder_type)

    def test_name_max_length(self):
        with self.assertRaises(me.errors.ValidationError):
            Folder.objects.create(
                name="A" * 51,
                folder_owner=self.user,
                folder_type=self.folder_type
            )

class FormStructureTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        data = random_user_data()
        self.user = CustomUser.objects.create(username=data["username"], email=data["email"])
        self.folder_type = FolderType.objects.create(type_name="Personal")
        self.folder = Folder.objects.create(
            name="MyFolder",
            folder_owner=self.user,
            folder_type=self.folder_type
        )
        self.column = FormStructureColumn(
            key_name="col1",
            title="Column 1",
            excel_column_name="col_1",
            content_type="str"
        )
        self.spec = FormStructureSpecifications(
            name="spec1",
            content="value1"
        )
        self.form_structure = FormStructure.objects.create(
            structure_name="TestForm",
            folder=self.folder,
            columns=[self.column],
            specifications=[self.spec]
        )

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_form_structure_creation(self):
        self.assertEqual(self.form_structure.structure_name, "TestForm")
        self.assertEqual(self.form_structure.folder, self.folder)
        self.assertEqual(self.form_structure.record_num, 0)
        self.assertEqual(len(self.form_structure.columns), 1)
        self.assertEqual(self.form_structure.columns[0].key_name, "col1")
        self.assertEqual(len(self.form_structure.specifications), 1)
        self.assertEqual(self.form_structure.specifications[0].name, "spec1")
        self.assertTrue(isinstance(self.form_structure.create_date, datetime))
        self.assertEqual(str(self.form_structure), "TestForm")

    def test_required_fields(self):
        with self.assertRaises(me.errors.ValidationError):
            FormStructure.objects.create(folder=self.folder)
        with self.assertRaises(me.errors.ValidationError):
            FormStructure.objects.create(structure_name="NoFolder")

    # def test_column_validation(self):
    #     with self.assertRaises(me.errors.ValidationError):
    #         col = FormStructureColumn(key_name="col1")  # Missing title
    #         col.full_clean()
    #     with self.assertRaises(me.errors.ValidationError):
    #         col = FormStructureColumn(title="Column 1")  # Missing key_name
    #         col.full_clean()
    #     with self.assertRaises(me.errors.ValidationError):
    #         col = FormStructureColumn(key_name="col1", title="Column 1", content_type="invalid")  # Invalid content_type
    #         col.full_clean()

class FormTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        data = random_user_data()
        self.user = CustomUser.objects.create(username=data["username"], email=data["email"])
        self.folder_type = FolderType.objects.create(type_name="Personal")
        self.folder = Folder.objects.create(
            name="MyFolder",
            folder_owner=self.user,
            folder_type=self.folder_type
        )
        self.form_structure = FormStructure.objects.create(
            structure_name="TestForm",
            folder=self.folder
        )
        self.form = Form.objects.create(
            form_structure=self.form_structure,
            user=self.user,
            form_name="TestFile"
        )

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_form_creation(self):
        self.assertEqual(self.form.form_structure, self.form_structure)
        self.assertEqual(self.form.user, self.user)
        self.assertEqual(self.form.form_name, "TestFile")
        self.assertTrue(isinstance(self.form.create_date, datetime))
        self.assertEqual(str(self.form), str(self.form.id))

    def test_required_fields(self):
        with self.assertRaises(me.errors.ValidationError):
            Form.objects.create(user=self.user)
        with self.assertRaises(me.errors.ValidationError):
            Form.objects.create(form_structure=self.form_structure)

class FormRecordTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        data = random_user_data()
        self.user = CustomUser.objects.create(username=data["username"], email=data["email"])
        self.folder_type = FolderType.objects.create(type_name="Personal")
        self.folder = Folder.objects.create(
            name="MyFolder",
            folder_owner=self.user,
            folder_type=self.folder_type
        )
        self.form_structure = FormStructure.objects.create(
            structure_name="TestForm",
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

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_form_record_creation(self):
        self.assertEqual(self.form_record.form, self.form)
        self.assertEqual(self.form_record.user, self.user)
        self.assertTrue(isinstance(self.form_record.create_date, datetime))
        self.assertEqual(str(self.form_record), str(self.form_record.id))

    def test_required_fields(self):
        with self.assertRaises(me.errors.ValidationError):
            FormRecord.objects.create(user=self.user)
        with self.assertRaises(me.errors.ValidationError):
            FormRecord.objects.create(form=self.form)

class FormRecordCellTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        data = random_user_data()
        self.user = CustomUser.objects.create(username=data["username"], email=data["email"])
        self.folder_type = FolderType.objects.create(type_name="Personal")
        self.folder = Folder.objects.create(
            name="MyFolder",
            folder_owner=self.user,
            folder_type=self.folder_type
        )
        self.column = FormStructureColumn(
            key_name="col1",
            title="Column 1",
            excel_column_name="col_1",
            content_type="str"
        )
        self.form_structure = FormStructure.objects.create(
            structure_name="TestForm",
            folder=self.folder,
            columns=[self.column]
        )
        self.form = Form.objects.create(
            form_structure=self.form_structure,
            user=self.user
        )
        self.form_record = FormRecord.objects.create(
            form=self.form,
            user=self.user
        )
        self.form_record_cell = FormRecordCell.objects.create(
            form_record=self.form_record,
            form_structure=self.form_structure,
            form_structure_column="col1",
            user=self.user,
            content="Test Content"
        )

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_form_record_cell_creation(self):
        self.assertEqual(self.form_record_cell.form_record, self.form_record)
        self.assertEqual(self.form_record_cell.form_structure, self.form_structure)
        self.assertEqual(self.form_record_cell.form_structure_column, "col1")
        self.assertEqual(self.form_record_cell.user, self.user)
        self.assertEqual(self.form_record_cell.content, "Test Content")
        self.assertTrue(isinstance(self.form_record_cell.create_date, datetime))
        self.assertEqual(str(self.form_record_cell), str(self.form_record_cell.id))

    def test_required_fields(self):
        with self.assertRaises(me.errors.ValidationError):
            FormRecordCell.objects.create(
                form_record=self.form_record,
                form_structure=self.form_structure,
                form_structure_column="col1",
                user=self.user
            )
        with self.assertRaises(me.errors.ValidationError):
            FormRecordCell.objects.create(
                form_structure=self.form_structure,
                form_structure_column="col1",
                user=self.user,
                content="Test"
            )
        with self.assertRaises(me.errors.ValidationError):
            FormRecordCell.objects.create(
                form_record=self.form_record,
                user=self.user,
                content="Test"
            )
        with self.assertRaises(me.errors.ValidationError):
            FormRecordCell.objects.create(
                form_record=self.form_record,
                form_structure_column="col1",
                user=self.user,
                content="Test"
            )

    def test_content_max_length(self):
        with self.assertRaises(me.errors.ValidationError):
            FormRecordCell.objects.create(
                form_record=self.form_record,
                form_structure=self.form_structure,
                form_structure_column="col1",
                user=self.user,
                content="A" * 251
            )


class UploadFileTests(TestCase):
    def setUp(self):
        me.disconnect()
        me.connect(
            'test_db',
            alias='default',
            mongo_client_class=mongomock.MongoClient
        )
        data = random_user_data()
        self.user = CustomUser.objects.create(username=data["username"], email=data["email"])
        self.folder_type = FolderType.objects.create(type_name="Personal")
        self.folder = Folder.objects.create(
            name="MyFolder",
            folder_owner=self.user,
            folder_type=self.folder_type
        )
        self.form_structure = FormStructure.objects.create(
            structure_name="TestForm",
            folder=self.folder
        )
        self.upload_file = UploadFile.objects.create(
            file_name="testfile.txt",
            user=self.user,
            form_structure=self.form_structure
        )

    def tearDown(self):
        me.get_connection(alias='default').drop_database('test_db')

    def test_upload_file_creation(self):
        self.assertEqual(self.upload_file.file_name, "testfile.txt")
        self.assertEqual(self.upload_file.user, self.user)
        self.assertEqual(self.upload_file.form_structure, self.form_structure)
        self.assertTrue(isinstance(self.upload_file.upload_date, datetime))
        self.assertEqual(str(self.upload_file), "testfile.txt")

    def test_required_fields(self):
        with self.assertRaises(me.errors.ValidationError):
            UploadFile.objects.create(user=self.user)
        with self.assertRaises(me.errors.ValidationError):
            UploadFile.objects.create(file_name="testfile.txt")

    def test_form_structure_optional(self):
        upload_file = UploadFile.objects.create(
            file_name="testfile_no_structure.txt",
            user=self.user
        )
        self.assertIsNone(upload_file.form_structure)
