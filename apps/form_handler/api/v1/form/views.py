from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404

from apps.form_handler.serializers import *


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
    عملیات CRUD برای فولدرها
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FolderSerializer
    queryset = Folder.objects.all()

    def get_queryset(self):
        return Folder.objects.all().order_by('-create_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return
        return FolderSerializer


class FolderTypeViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FolderType CRUD operations
    عملیات CRUD برای تایپ‌های فولدر
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FolderTypeSerializer
    queryset = FolderType.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return FolderTypeListSerializer
        return FolderTypeSerializer


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
    عملیات CRUD برای ساختار فرم‌ها
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


class FormStructureColumnViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FormStructureColumn CRUD operations
    عملیات CRUD برای ستون‌های ساختار فرم (تعبیه‌شده)
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


class FormStructureSpecificationViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    ViewSet for FormStructureSpecification CRUD operations
    عملیات CRUD برای مشخصات ساختار فرم (تعبیه‌شده)
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
    عملیات CRUD برای فرم‌ها
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
    عملیات CRUD برای رکوردهای فرم
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
    عملیات CRUD برای سلول‌های رکورد فرم
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
    عملیات CRUD برای فایل‌های آپلودشده
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer
    queryset = UploadFile.objects.all()

    def get_queryset(self):
        return UploadFile.objects.all().order_by('-upload_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return UploadFileSerializer  # No separate list serializer needed
        return UploadFileSerializer
