from django.http import Http404
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from apps.form_handler.documents import (
    Folder, FolderType, FormStructure, Form, FormRecord, FormRecordCell, UploadFile
)
from apps.form_handler.serializers import (
    FolderSerializer, FolderTypeSerializer, FolderTypeListSerializer,
    FormStructureSerializer, FormStructureListSerializer, FormStructureColumnSerializer,
    FormStructureSpecificationsSerializer, FormSerializer, FormListSerializer,
    FormRecordSerializer, FormRecordListSerializer, FormRecordCellSerializer,
    FormRecordCellListSerializer, UploadFileSerializer
)
from apps.form_handler.api.v1.form.swagger_decorator import (
    folder_create_swagger, folder_retrieve_swagger, folder_update_swagger,
    folder_partial_update_swagger, folder_destroy_swagger, folder_list_swagger,
    folder_type_create_swagger, folder_type_list_swagger, folder_type_update_swagger,
    folder_type_destroy_swagger, form_structure_create_swagger, form_structure_retrieve_swagger,
    form_structure_update_swagger, form_structure_partial_update_swagger,
    form_structure_destroy_swagger, form_structure_list_swagger,
    form_structure_column_create_swagger, form_structure_column_list_swagger,
    form_structure_column_update_swagger, form_structure_column_destroy_swagger,
    form_structure_spec_create_swagger, form_structure_spec_list_swagger,
    form_structure_spec_update_swagger, form_structure_spec_destroy_swagger,
    form_create_swagger, form_retrieve_swagger, form_update_swagger,
    form_partial_update_swagger, form_destroy_swagger, form_list_swagger,
    form_record_create_swagger, form_record_retrieve_swagger, form_record_update_swagger,
    form_record_partial_update_swagger, form_record_destroy_swagger, form_record_list_swagger,
    form_record_cell_create_swagger, form_record_cell_retrieve_swagger,
    form_record_cell_update_swagger, form_record_cell_partial_update_swagger,
    form_record_cell_destroy_swagger, form_record_cell_list_swagger,
    upload_file_create_swagger, upload_file_retrieve_swagger, upload_file_update_swagger,
    upload_file_partial_update_swagger, upload_file_destroy_swagger, upload_file_list_swagger,
)

@method_decorator(name='create', decorator=folder_create_swagger)
@method_decorator(name='retrieve', decorator=folder_retrieve_swagger)
@method_decorator(name='update', decorator=folder_update_swagger)
@method_decorator(name='partial_update', decorator=folder_partial_update_swagger)
@method_decorator(name='destroy', decorator=folder_destroy_swagger)
@method_decorator(name='list', decorator=folder_list_swagger)
class FolderViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing Folder records with full CRUD operations.
    Orders folders by creation date in descending order.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FolderSerializer
    queryset = Folder.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        """
        Returns all Folder objects ordered by creation date (newest first).
        """
        return self.queryset.order_by('-create_date')

@method_decorator(name='create', decorator=folder_type_create_swagger)
@method_decorator(name='list', decorator=folder_type_list_swagger)
@method_decorator(name='update', decorator=folder_type_update_swagger)
@method_decorator(name='destroy', decorator=folder_type_destroy_swagger)
class FolderTypeViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing FolderType records with CRUD operations.
    Uses specialized serializer for list action.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FolderTypeSerializer
    queryset = FolderType.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        """
        Returns FolderTypeListSerializer for list action, otherwise FolderTypeSerializer.
        """
        return FolderTypeListSerializer if self.action == 'list' else self.serializer_class

@method_decorator(name='create', decorator=form_structure_create_swagger)
@method_decorator(name='retrieve', decorator=form_structure_retrieve_swagger)
@method_decorator(name='update', decorator=form_structure_update_swagger)
@method_decorator(name='partial_update', decorator=form_structure_partial_update_swagger)
@method_decorator(name='destroy', decorator=form_structure_destroy_swagger)
@method_decorator(name='list', decorator=form_structure_list_swagger)
class FormStructureViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing FormStructure records with CRUD operations.
    Filters by folder if folder_pk is provided in URL, orders by creation date.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormStructureSerializer
    queryset = FormStructure.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        """
        Filters FormStructure by folder_pk if provided, otherwise returns all ordered by creation date.
        """
        folder_pk = self.kwargs.get('folder_pk')
        queryset = self.queryset.order_by('-create_date')
        return queryset.filter(folder=folder_pk) if folder_pk else queryset

    def get_serializer_class(self):
        """
        Returns FormStructureListSerializer for list action, otherwise FormStructureSerializer.
        """
        return FormStructureListSerializer if self.action == 'list' else self.serializer_class

@method_decorator(name='create', decorator=form_structure_column_create_swagger)
@method_decorator(name='list', decorator=form_structure_column_list_swagger)
@method_decorator(name='update', decorator=form_structure_column_update_swagger)
@method_decorator(name='destroy', decorator=form_structure_column_destroy_swagger)
class FormStructureColumnViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing FormStructureColumn records embedded in FormStructure.
    Handles CRUD operations for columns within a specific FormStructure.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormStructureColumnSerializer
    lookup_field = 'pk'

    def get_form_structure(self):
        """
        Retrieves FormStructure by ID from URL kwargs, raises Http404 if not found.
        """
        form_structure_id = self.kwargs.get('form_structure_id')
        try:
            return FormStructure.objects.get(id=form_structure_id)
        except FormStructure.DoesNotExist:
            raise Http404("FormStructure not found")

    def get_queryset(self):
        """
        Returns columns associated with the specified FormStructure.
        """
        return self.get_form_structure().columns

    def perform_create(self, serializer):
        """
        Creates a new column and appends it to the FormStructure's columns list.
        """
        form_structure = self.get_form_structure()
        column = serializer.save()
        form_structure.columns.append(column)
        form_structure.save()

    def get_object(self):
        """
        Retrieves a specific column by index from FormStructure's columns list.
        Raises Http404 if index is invalid.
        """
        form_structure = self.get_form_structure()
        try:
            return form_structure.columns[int(self.kwargs.get('pk'))]
        except (IndexError, ValueError):
            raise Http404("Column not found")

    def perform_update(self, serializer):
        """
        Updates a column and saves the parent FormStructure.
        """
        form_structure = self.get_form_structure()
        serializer.save()
        form_structure.save()

    def perform_destroy(self, instance):
        """
        Deletes a column from FormStructure's columns list and saves the parent.
        """
        form_structure = self.get_form_structure()
        serializer = self.get_serializer(instance)
        serializer.delete(instance, form_structure)

@method_decorator(name='create', decorator=form_structure_spec_create_swagger)
@method_decorator(name='list', decorator=form_structure_spec_list_swagger)
@method_decorator(name='update', decorator=form_structure_spec_update_swagger)
@method_decorator(name='destroy', decorator=form_structure_spec_destroy_swagger)
class FormStructureSpecificationViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing FormStructureSpecification records embedded in FormStructure.
    Handles CRUD operations for specifications within a specific FormStructure.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormStructureSpecificationsSerializer
    lookup_field = 'pk'

    def get_form_structure(self):
        """
        Retrieves FormStructure by ID from URL kwargs, raises Http404 if not found.
        """
        form_structure_id = self.kwargs.get('form_structure_id')
        try:
            return FormStructure.objects.get(id=form_structure_id)
        except FormStructure.DoesNotExist:
            raise Http404("FormStructure not found")

    def get_queryset(self):
        """
        Returns specifications associated with the specified FormStructure.
        """
        return self.get_form_structure().specifications

    def perform_create(self, serializer):
        """
        Creates a new specification and appends it to the FormStructure's specifications list.
        """
        form_structure = self.get_form_structure()
        specification = serializer.save()
        form_structure.specifications.append(specification)
        form_structure.save()

    def get_object(self):
        """
        Retrieves a specific specification by index from FormStructure's specifications list.
        Raises Http404 if index is invalid.
        """
        form_structure = self.get_form_structure()
        try:
            return form_structure.specifications[int(self.kwargs.get('pk'))]
        except (IndexError, ValueError):
            raise Http404("Specification not found")

    def perform_update(self, serializer):
        """
        Updates a specification and saves the parent FormStructure.
        """
        form_structure = self.get_form_structure()
        serializer.save()
        form_structure.save()

    def perform_destroy(self, instance):
        """
        Deletes a specification from FormStructure's specifications list and saves the parent.
        """
        form_structure = self.get_form_structure()
        serializer = self.get_serializer(instance)
        serializer.delete(instance, form_structure)

@method_decorator(name='create', decorator=form_create_swagger)
@method_decorator(name='retrieve', decorator=form_retrieve_swagger)
@method_decorator(name='update', decorator=form_update_swagger)
@method_decorator(name='partial_update', decorator=form_partial_update_swagger)
@method_decorator(name='destroy', decorator=form_destroy_swagger)
@method_decorator(name='list', decorator=form_list_swagger)
class FormViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing Form records with full CRUD operations.
    Orders forms by creation date in descending order.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormSerializer
    queryset = Form.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        """
        Returns all Form objects ordered by creation date (newest first).
        """
        return self.queryset.order_by('-create_date')

    def get_serializer_class(self):
        """
        Returns FormListSerializer for list action, otherwise FormSerializer.
        """
        return FormListSerializer if self.action == 'list' else self.serializer_class

@method_decorator(name='create', decorator=form_record_create_swagger)
@method_decorator(name='retrieve', decorator=form_record_retrieve_swagger)
@method_decorator(name='update', decorator=form_record_update_swagger)
@method_decorator(name='partial_update', decorator=form_record_partial_update_swagger)
@method_decorator(name='destroy', decorator=form_record_destroy_swagger)
@method_decorator(name='list', decorator=form_record_list_swagger)
class FormRecordViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing FormRecord records with full CRUD operations.
    Orders records by creation date in descending order.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormRecordSerializer
    queryset = FormRecord.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        """
        Returns all FormRecord objects ordered by creation date (newest first).
        """
        return self.queryset.order_by('-create_date')

    def get_serializer_class(self):
        """
        Returns FormRecordListSerializer for list action, otherwise FormRecordSerializer.
        """
        return FormRecordListSerializer if self.action == 'list' else self.serializer_class

@method_decorator(name='create', decorator=form_record_cell_create_swagger)
@method_decorator(name='retrieve', decorator=form_record_cell_retrieve_swagger)
@method_decorator(name='update', decorator=form_record_cell_update_swagger)
@method_decorator(name='partial_update', decorator=form_record_cell_partial_update_swagger)
@method_decorator(name='destroy', decorator=form_record_cell_destroy_swagger)
@method_decorator(name='list', decorator=form_record_cell_list_swagger)
class FormRecordCellViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing FormRecordCell records with full CRUD operations.
    Orders cells by creation date in descending order.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormRecordCellSerializer
    queryset = FormRecordCell.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        """
        Returns all FormRecordCell objects ordered by creation date (newest first).
        """
        return self.queryset.order_by('-create_date')

    def get_serializer_class(self):
        """
        Returns FormRecordCellListSerializer for list action, otherwise FormRecordCellSerializer.
        """
        return FormRecordCellListSerializer if self.action == 'list' else self.serializer_class

@method_decorator(name='create', decorator=upload_file_create_swagger)
@method_decorator(name='retrieve', decorator=upload_file_retrieve_swagger)
@method_decorator(name='update', decorator=upload_file_update_swagger)
@method_decorator(name='partial_update', decorator=upload_file_partial_update_swagger)
@method_decorator(name='destroy', decorator=upload_file_destroy_swagger)
@method_decorator(name='list', decorator=upload_file_list_swagger)
class UploadFileViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for managing UploadFile records with full CRUD operations.
    Orders files by upload date in descending order.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer
    queryset = UploadFile.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        """
        Returns all UploadFile objects ordered by upload date (newest first).
        """
        return self.queryset.order_by('-upload_date')