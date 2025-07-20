# import mongomock
# import random
# import string
# from django.test import TestCase
# from mongoengine import connect, disconnect
# from unittest.mock import patch
#
# from apps.form_handler.documents import (
#     CustomUser,
#     FolderType,
#     Folder,
#     FormStructure,
#     Form,
#     FormRecord,
#     FormRecordCell,
#     UploadFile,
# )
# from apps.form_handler.serializers import (
#     CustomUserSerializer,
#     FolderTypeSerializer,
#     FolderSerializer,
#     FormStructureSerializer,
#     FormSerializer,
#     FormRecordSerializer,
#     FormRecordCellSerializer,
#     UploadFileSerializer,
# )
#
# def random_username():
#     return 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
#
# def random_email():
#     return ''.join(random.choices(string.ascii_lowercase, k=6)) + '@example.com'
#
# class SerializerTestCase(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         disconnect()
#         super().setUpClass()
#         connect(
#             db='testdb',
#             host='mongodb://localhost',
#             # mongo_client_class=mongomock.MongoClient  # اگر می‌خواهید کاملاً تستی باشد این خط را فعال کنید
#         )
#
#     @classmethod
#     def tearDownClass(cls):
#         disconnect()
#         super().tearDownClass()
#
#     def setUp(self):
#         self.user = CustomUser.objects.create(
#             username=random_username(),
#             email=random_email()
#         )
#         self.folder_type = FolderType.objects.create(type_name='test_type')
#         self.folder = Folder.objects.create(
#             name='test_folder',
#             folder_owner=self.user,
#             folder_type=self.folder_type
#         )
#         self.form_structure = FormStructure.objects.create(
#             structure_name='test_structure',
#             folder=self.folder
#         )
#         self.form = Form.objects.create(
#             form_structure=self.form_structure,
#             user=self.user
#         )
#         self.form_record = FormRecord.objects.create(
#             form=self.form,
#             user=self.user
#         )
#
# class CustomUserSerializerTest(SerializerTestCase):
#     def test_serializer(self):
#         serializer = CustomUserSerializer(instance=self.user)
#         self.assertEqual(serializer.data['username'], self.user.username)
#
# class FolderTypeSerializerTest(SerializerTestCase):
#     def test_serializer(self):
#         serializer = FolderTypeSerializer(instance=self.folder_type)
#         self.assertEqual(serializer.data['type_name'], self.folder_type.type_name)
#
# class FolderSerializerTest(SerializerTestCase):
#     def test_serializer(self):
#         serializer = FolderSerializer(instance=self.folder)
#         self.assertEqual(serializer.data['name'], self.folder.name)
#
# class FormStructureSerializerTest(SerializerTestCase):
#     def test_serializer(self):
#         serializer = FormStructureSerializer(instance=self.form_structure)
#         self.assertEqual(serializer.data['structure_name'], self.form_structure.structure_name)
#
# class FormSerializerTest(SerializerTestCase):
#     def test_serializer(self):
#         serializer = FormSerializer(instance=self.form)
#         self.assertEqual(serializer.data['form_structure'], str(self.form_structure.id))
#
# class FormRecordSerializerTest(SerializerTestCase):
#     def test_serializer(self):
#         serializer = FormRecordSerializer(instance=self.form_record)
#         self.assertEqual(serializer.data['form'], str(self.form.id))
#
# def test_serializer(self):
#     cell = FormRecordCell.objects.create(
#         form_record=self.form_record,
#         form_structure=self.form_structure,
#         form_structure_column='some_column_name',  # اینجا باید string بدی، نه آبجکت
#         user=self.user,
#         content='test content'
#     )
#     serializer = FormRecordCellSerializer(instance=cell)
#     self.assertEqual(serializer.data['content'], cell.content)
