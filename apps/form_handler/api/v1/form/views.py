from django.http import Http404
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.form_handler.serializers import *


# Swagger Decorators
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new folder',
    tags=['form_handler.form'],
    request_body=FolderSerializer,
    responses={201: FolderSerializer}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary='Retrieve a folder',
    tags=['form_handler.form'],
    responses={200: FolderSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a folder',
    tags=['form_handler.form'],
    request_body=FolderSerializer,
    responses={200: FolderSerializer}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary='Partially update a folder',
    tags=['form_handler.form'],
    request_body=FolderSerializer,
    responses={200: FolderSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a folder',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all folders',
    tags=['form_handler.form'],
    responses={200: FolderListSerializer(many=True)}
))
class FolderViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for Folder CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FolderSerializer
    queryset = Folder.objects.all()

    def get_queryset(self):
        return Folder.objects.all().order_by('-create_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return FolderListSerializer
        return FolderSerializer


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new folder type',
    tags=['form_handler.form'],
    request_body=FolderTypeSerializer,
    responses={201: FolderTypeSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a folder type',
    tags=['form_handler.form'],
    request_body=FolderTypeSerializer,
    responses={200: FolderTypeSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a folder type',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all folder types',
    tags=['form_handler.form'],
    responses={200: FolderTypeListSerializer(many=True)}
))
class FolderTypeViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FolderType CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FolderTypeSerializer
    queryset = FolderType.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return FolderTypeListSerializer
        return FolderTypeSerializer


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new form structure',
    tags=['form_handler.form'],
    request_body=FormStructureSerializer,
    responses={201: FormStructureSerializer}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary='Retrieve a form structure',
    tags=['form_handler.form'],
    responses={200: FormStructureSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a form structure',
    tags=['form_handler.form'],
    request_body=FormStructureSerializer,
    responses={200: FormStructureSerializer}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary='Partially update a form structure',
    tags=['form_handler.form'],
    request_body=FormStructureSerializer,
    responses={200: FormStructureSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a form structure',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all form structures',
    tags=['form_handler.form'],
    responses={200: FormStructureListSerializer(many=True)}
))
class FormStructureViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FormStructure CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormStructureSerializer
    queryset = FormStructure.objects.all()

    def get_queryset(self):
        folder_pk = self.kwargs.get('folder_pk')
        if folder_pk:
            return FormStructure.objects.filter(folder=folder_pk).order_by('-create_date')
        return FormStructure.objects.all().order_by('-create_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return FormStructureListSerializer
        return FormStructureSerializer


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new form structure column',
    tags=['form_handler.form'],
    request_body=FormStructureColumnSerializer,
    responses={201: FormStructureColumnSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a form structure column',
    tags=['form_handler.form'],
    request_body=FormStructureColumnSerializer,
    responses={200: FormStructureColumnSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a form structure column',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all form structure columns',
    tags=['form_handler.form'],
    responses={200: FormStructureColumnSerializer(many=True)}
))
class FormStructureColumnViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FormStructureColumn CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormStructureColumnSerializer

    def get_form_structure(self):
        form_structure_id = self.kwargs.get('form_structure_id')
        try:
            return FormStructure.objects.get(id=form_structure_id)
        except FormStructure.DoesNotExist:
            raise Http404("FormStructure not found")

    def get_queryset(self):
        return self.get_form_structure().columns

    def perform_create(self, serializer):
        form_structure = self.get_form_structure()
        column = serializer.save()
        form_structure.columns.append(column)
        form_structure.save()

    def get_object(self):
        form_structure = self.get_form_structure()
        column_index = int(self.kwargs.get('pk'))  # Assuming pk is the index in the columns list
        try:
            return form_structure.columns[column_index]
        except IndexError:
            raise Http404("Column not found")

    def perform_update(self, serializer):
        form_structure = self.get_form_structure()
        serializer.save()
        form_structure.save()

    def perform_destroy(self, instance):
        form_structure = self.get_form_structure()
        serializer = self.get_serializer(instance)
        serializer.delete(instance, form_structure)


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new form structure specification',
    tags=['form_handler.form'],
    request_body=FormStructureSpecificationsSerializer,
    responses={201: FormStructureSpecificationsSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a form structure specification',
    tags=['form_handler.form'],
    request_body=FormStructureSpecificationsSerializer,
    responses={200: FormStructureSpecificationsSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a form structure specification',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all form structure specifications',
    tags=['form_handler.form'],
    responses={200: FormStructureSpecificationsSerializer(many=True)}
))
class FormStructureSpecificationViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FormStructureSpecification CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormStructureSpecificationsSerializer

    def get_form_structure(self):
        form_structure_id = self.kwargs.get('form_structure_id')
        try:
            return FormStructure.objects.get(id=form_structure_id)
        except FormStructure.DoesNotExist:
            raise Http404("FormStructure not found")

    def get_queryset(self):
        return self.get_form_structure().specifications

    def perform_create(self, serializer):
        form_structure = self.get_form_structure()
        specification = serializer.save()
        form_structure.specifications.append(specification)
        form_structure.save()

    def get_object(self):
        form_structure = self.get_form_structure()
        specification_index = int(self.kwargs.get('pk'))  # Assuming pk is the index in the specifications list
        try:
            return form_structure.specifications[specification_index]
        except IndexError:
            raise Http404("Specification not found")

    def perform_update(self, serializer):
        form_structure = self.get_form_structure()
        serializer.save()
        form_structure.save()

    def perform_destroy(self, instance):
        form_structure = self.get_form_structure()
        serializer = self.get_serializer(instance)
        serializer.delete(instance, form_structure)


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new form',
    tags=['form_handler.form'],
    request_body=FormSerializer,
    responses={201: FormSerializer}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary='Retrieve a form',
    tags=['form_handler.form'],
    responses={200: FormSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a form',
    tags=['form_handler.form'],
    request_body=FormSerializer,
    responses={200: FormSerializer}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary='Partially update a form',
    tags=['form_handler.form'],
    request_body=FormSerializer,
    responses={200: FormSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a form',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all forms',
    tags=['form_handler.form'],
    responses={200: FormListSerializer(many=True)}
))
class FormViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for Form CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormSerializer
    queryset = Form.objects.all()

    def get_queryset(self):
        return Form.objects.all().order_by('-create_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return FormListSerializer
        return FormSerializer


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new form record',
    tags=['form_handler.form'],
    request_body=FormRecordSerializer,
    responses={201: FormRecordSerializer}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary='Retrieve a form record',
    tags=['form_handler.form'],
    responses={200: FormRecordSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a form record',
    tags=['form_handler.form'],
    request_body=FormRecordSerializer,
    responses={200: FormRecordSerializer}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary='Partially update a form record',
    tags=['form_handler.form'],
    request_body=FormRecordSerializer,
    responses={200: FormRecordSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a form record',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all form records',
    tags=['form_handler.form'],
    responses={200: FormRecordListSerializer(many=True)}
))
class FormRecordViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FormRecord CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormRecordSerializer
    queryset = FormRecord.objects.all()

    def get_queryset(self):
        return FormRecord.objects.all().order_by('-create_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return FormRecordListSerializer
        return FormRecordSerializer


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new form record cell',
    tags=['form_handler.form'],
    request_body=FormRecordCellSerializer,
    responses={201: FormRecordCellSerializer}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary='Retrieve a form record cell',
    tags=['form_handler.form'],
    responses={200: FormRecordCellSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update a form record cell',
    tags=['form_handler.form'],
    request_body=FormRecordCellSerializer,
    responses={200: FormRecordCellSerializer}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary='Partially update a form record cell',
    tags=['form_handler.form'],
    request_body=FormRecordCellSerializer,
    responses={200: FormRecordCellSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete a form record cell',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all form record cells',
    tags=['form_handler.form'],
    responses={200: FormRecordCellListSerializer(many=True)}
))
class FormRecordCellViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FormRecordCell CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormRecordCellSerializer
    queryset = FormRecordCell.objects.all()

    def get_queryset(self):
        return FormRecordCell.objects.all().order_by('-create_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return FormRecordCellListSerializer
        return FormRecordCellSerializer


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Create a new upload file',
    tags=['form_handler.form'],
    request_body=UploadFileSerializer,
    responses={201: UploadFileSerializer}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_summary='Retrieve an upload file',
    tags=['form_handler.form'],
    responses={200: UploadFileSerializer}
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_summary='Update an upload file',
    tags=['form_handler.form'],
    request_body=UploadFileSerializer,
    responses={200: UploadFileSerializer}
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_summary='Partially update an upload file',
    tags=['form_handler.form'],
    request_body=UploadFileSerializer,
    responses={200: UploadFileSerializer}
))
@method_decorator(name='destroy', decorator=swagger_auto_schema(
    operation_summary='Delete an upload file',
    tags=['form_handler.form'],
    responses={204: 'No Content'}
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all upload files',
    tags=['form_handler.form'],
    responses={200: UploadFileSerializer(many=True)}
))
class UploadFileViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for UploadFile CRUD operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer
    queryset = UploadFile.objects.all()

    def get_queryset(self):
        return UploadFile.objects.all().order_by('-upload_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return UploadFileSerializer
        return UploadFileSerializer
