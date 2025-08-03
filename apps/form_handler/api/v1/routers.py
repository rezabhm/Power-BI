from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.form_handler.api.v1.form.views import *
from apps.form_handler.api.v1.reporting.views import *
from apps.form_handler.api.v1.upload_file.views import *

router = DefaultRouter()
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'folder-types', FolderTypeViewSet, basename='folder-type')
router.register(r'form-structures', FormStructureViewSet, basename='form-structure')
router.register(r'form-structures/(?P<form_structure_id>[^/.]+)/columns', FormStructureColumnViewSet, basename='form-structure-column')
router.register(r'form-structures/(?P<form_structure_id>[^/.]+)/specifications', FormStructureSpecificationViewSet, basename='form-structure-specification')
router.register(r'forms', FormViewSet, basename='form')
router.register(r'form-records', FormRecordViewSet, basename='form-record')
router.register(r'form-record-cells', FormRecordCellViewSet, basename='form-record-cell')

router.register(r'upload-files', UploadFileViewSet, basename='upload-file')
router.register(r'filter-config', FilterConfigViewSet, basename='filter-config')
router.register(r'form-structure-reporting', FormStructureReportingViewSet, basename='form-structure-reporting')

urlpatterns = [
    path('', include(router.urls)),
    path('folders/<str:folder_pk>/form-structures/', FormStructureViewSet.as_view({'get': 'list'}), name='form-structure-list-by-folder'),
]