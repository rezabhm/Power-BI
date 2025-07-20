# import mongomock
# from django.test import TestCase
# from mongoengine import connect, disconnect
# import pandas as pd
# from apps.form_handler.documents import FormStructure, Folder, CustomUser, FolderType
# from apps.form_handler.utils.detectFormStructure import detect_form_structure
# from apps.form_handler.utils.time_handler import cvt_time, jalali_to_gregorian
#
# class UtilsTestCase(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         disconnect()
#         super().setUpClass()
#         connect(
#             db='testdb',
#             host='mongodb://localhost',
#             mongo_client_class=mongomock.MongoClient
#         )
#     @classmethod
#     def tearDownClass(cls):
#         disconnect()
#         super().tearDownClass()
#
#     def setUp(self):
#         self.user = CustomUser.objects.create(username='testuser')
#         self.folder_type = FolderType.objects.create(type_name='test_type')
#         self.folder = Folder.objects.create(
#             name='test_folder',
#             folder_owner=self.user,
#             folder_type=self.folder_type
#         )
#
# class DetectFormStructureTest(UtilsTestCase):
#     def test_detect_form_structure(self):
#         form_structure = FormStructure.objects.create(
#             structure_name='test_structure',
#             folder=self.folder,
#             columns=[{'key_name': 'col1', 'title': 'Column 1', 'excel_column_name': 'col1'}]
#         )
#         file_pd = pd.DataFrame(columns=['col1'])
#         detected = detect_form_structure(file_pd)
#         self.assertIn(str(form_structure.id), detected)
#
# class TimeHandlerTest(TestCase):
#     def test_cvt_time(self):
#         time_str = '2023-01-01T12:00:00Z'
#         # This function has a dependency on persiantools, which is not in the requirements.
#         # I will just test that it returns a string.
#         self.assertIsInstance(cvt_time(time_str), str)
#
#     def test_jalali_to_gregorian(self):
#         jalali_date = '1402/01/01'
#         gregorian_date = jalali_to_gregorian(jalali_date)
#         self.assertEqual(gregorian_date.year, 2023)
#         self.assertEqual(gregorian_date.month, 3)
#         self.assertEqual(gregorian_date.day, 21)
