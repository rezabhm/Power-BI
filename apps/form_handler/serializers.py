import os
import random
from typing import Any, Dict
from bson import ObjectId
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer

from apps.core.documents import CustomUser
from apps.form_handler.documents import (
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
from apps.form_handler.utils.time_handler import cvt_time
import logging

# Configure logging
logger = logging.getLogger(__name__)


class FolderTypeSerializer(DocumentSerializer):
    """
    Serializer for FolderType model, handling folder type data.
    """
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FolderType
        fields = ['id', 'type_name']

    def to_representation(self, instance: FolderType) -> Dict[str, Any]:
        """
        Converts ObjectId to string for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        return data

class FolderTypeListSerializer(FolderTypeSerializer):
    """
    Serializer for listing FolderType objects, reusing base FolderTypeSerializer.
    """
    class Meta(FolderTypeSerializer.Meta):
        pass

class FolderSerializer(DocumentSerializer):
    """
    Serializer for Folder model, handling folder creation and updates.
    """
    id = serializers.CharField(read_only=True)
    folder_owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    folder_type = serializers.PrimaryKeyRelatedField(queryset=FolderType.objects.all())

    class Meta:
        model = Folder
        fields = ['id', 'name', 'create_date', 'folder_owner', 'folder_type']

    def to_representation(self, instance: Folder) -> Dict[str, Any]:
        """
        Converts ObjectId fields to strings for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        data['folder_owner'] = str(data['folder_owner']) if isinstance(data.get('folder_owner'), ObjectId) else data['folder_owner']
        data['folder_type'] = str(data['folder_type']) if isinstance(data.get('folder_type'), ObjectId) else data['folder_type']
        return data

class FolderListSerializer(DocumentSerializer):
    """
    Serializer for listing Folder objects with minimal fields.
    """
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'create_date']

    def to_representation(self, instance: Folder) -> Dict[str, Any]:
        """
        Converts ObjectId to string for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        return data

class FormStructureColumnSerializer(serializers.Serializer):
    """
    Serializer for FormStructureColumn embedded document.
    """
    key_name = serializers.CharField(max_length=50, required=True)
    title = serializers.CharField(max_length=50, required=True)
    excel_column_name = serializers.CharField(max_length=50, required=False, default='column')
    content_type = serializers.ChoiceField(choices=['str', 'int', 'bool', 'float', 'date'], default='str')

    def create(self, validated_data: Dict[str, Any]) -> FormStructureColumn:
        """
        Creates a FormStructureColumn instance from validated data.
        """
        return FormStructureColumn(**validated_data)

    def update(self, instance: FormStructureColumn, validated_data: Dict[str, Any]) -> FormStructureColumn:
        """
        Updates an existing FormStructureColumn instance with validated data.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        return instance

class FormStructureColumnListSerializer(serializers.ListSerializer):
    """
    List serializer for FormStructureColumn objects.
    """
    child = FormStructureColumnSerializer()

class FormStructureSpecificationsSerializer(serializers.Serializer):
    """
    Serializer for FormStructureSpecifications embedded document.
    """
    name = serializers.CharField(max_length=50, required=True)
    content = serializers.CharField(max_length=50, required=True)

    def create(self, validated_data: Dict[str, Any]) -> FormStructureSpecifications:
        """
        Creates a FormStructureSpecifications instance from validated data.
        """
        return FormStructureSpecifications(**validated_data)

    def update(self, instance: FormStructureSpecifications, validated_data: Dict[str, Any]) -> FormStructureSpecifications:
        """
        Updates an existing FormStructureSpecifications instance with validated data.
        """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        return instance

class FormStructureSpecificationsListSerializer(serializers.ListSerializer):
    """
    List serializer for FormStructureSpecifications objects.
    """
    child = FormStructureSpecificationsSerializer()

class FormStructureSerializer(DocumentSerializer):
    """
    Serializer for FormStructure model, handling form structure creation and updates.
    """
    id = serializers.CharField(read_only=True)
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
    columns = FormStructureColumnSerializer(many=True, required=False)
    specifications = FormStructureSpecificationsSerializer(many=True, required=False)

    class Meta:
        model = FormStructure
        fields = ['id', 'structure_name', 'create_date', 'folder', 'record_num', 'columns', 'specifications']

    def to_representation(self, instance: FormStructure) -> Dict[str, Any]:
        """
        Converts ObjectId fields to strings for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        data['folder'] = str(data['folder']) if isinstance(data.get('folder'), ObjectId) else data['folder']
        return data

    def create(self, validated_data: Dict[str, Any]) -> FormStructure:
        """
        Creates a FormStructure instance with embedded columns and specifications.
        """
        columns_data = validated_data.pop('columns', [])
        specifications_data = validated_data.pop('specifications', [])
        try:
            form_structure = FormStructure(**validated_data)
            form_structure.columns = [FormStructureColumn(**column) for column in columns_data]
            form_structure.specifications = [FormStructureSpecifications(**spec) for spec in specifications_data]
            form_structure.save()
            logger.info("Created FormStructure with ID: %s", form_structure.id)
            return form_structure
        except Exception as e:
            logger.error("Failed to create FormStructure: %s", str(e))
            raise serializers.ValidationError(f"Error creating FormStructure: {str(e)}")

    def update(self, instance: FormStructure, validated_data: Dict[str, Any]) -> FormStructure:
        """
        Updates an existing FormStructure instance with validated data.
        """
        try:
            instance.structure_name = validated_data.get('structure_name', instance.structure_name)
            instance.folder = validated_data.get('folder', instance.folder)
            instance.record_num = validated_data.get('record_num', instance.record_num)
            if 'columns' in validated_data:
                instance.columns = [FormStructureColumn(**column) for column in validated_data['columns']]
            if 'specifications' in validated_data:
                instance.specifications = [FormStructureSpecifications(**spec) for spec in validated_data['specifications']]
            instance.save()
            logger.info("Updated FormStructure with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update FormStructure with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating FormStructure: {str(e)}")

class FormStructureListSerializer(DocumentSerializer):
    """
    Serializer for listing FormStructure objects with minimal fields.
    """
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FormStructure
        fields = ['id', 'structure_name', 'create_date', 'record_num']

    def to_representation(self, instance: FormStructure) -> Dict[str, Any]:
        """
        Converts ObjectId to string for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        return data

class FormSerializer(DocumentSerializer):
    """
    Serializer for Form model, handling form creation and updates.
    """
    id = serializers.CharField(read_only=True)
    form_structure = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Form
        fields = ['id', 'form_structure', 'user', 'create_date', 'form_name']

    def to_representation(self, instance: Form) -> Dict[str, Any]:
        """
        Converts ObjectId fields to strings for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        data['form_structure'] = str(data['form_structure']) if isinstance(data.get('form_structure'), ObjectId) else data['form_structure']
        data['user'] = str(data['user']) if isinstance(data.get('user'), ObjectId) else data['user']
        return data

class FormListSerializer(DocumentSerializer):
    """
    Serializer for listing Form objects with minimal fields.
    """
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'form_name', 'create_date']

    def to_representation(self, instance: Form) -> Dict[str, Any]:
        """
        Converts ObjectId to string for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        return data

class FormRecordSerializer(DocumentSerializer):
    """
    Serializer for FormRecord model, handling form record creation and updates.
    """
    id = serializers.CharField(read_only=True)
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = FormRecord
        fields = ['id', 'form', 'create_date', 'user']

    def to_representation(self, instance: FormRecord) -> Dict[str, Any]:
        """
        Converts ObjectId fields to strings for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        data['form'] = str(data['form']) if isinstance(data.get('form'), ObjectId) else data['form']
        data['user'] = str(data['user']) if isinstance(data.get('user'), ObjectId) else data['user']
        return data

class FormRecordListSerializer(DocumentSerializer):
    """
    Serializer for listing FormRecord objects with minimal fields.
    """
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FormRecord
        fields = ['id', 'create_date']

    def to_representation(self, instance: FormRecord) -> Dict[str, Any]:
        """
        Converts ObjectId to string for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        return data

class FormRecordCellSerializer(DocumentSerializer):
    """
    Serializer for FormRecordCell model, handling form record cell creation and updates.
    """
    id = serializers.CharField(read_only=True)
    form_record = serializers.PrimaryKeyRelatedField(queryset=FormRecord.objects.all())
    form_structure_column = serializers.CharField(max_length=50)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = FormRecordCell
        fields = ['id', 'form_record', 'form_structure_column', 'create_date', 'user', 'content']

    def to_representation(self, instance: FormRecordCell) -> Dict[str, Any]:
        """
        Converts ObjectId fields to strings for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        data['form_record'] = str(data['form_record']) if isinstance(data.get('form_record'), ObjectId) else data['form_record']
        data['user'] = str(data['user']) if isinstance(data.get('user'), ObjectId) else data['user']
        return data

class FormRecordCellListSerializer(DocumentSerializer):
    """
    Serializer for listing FormRecordCell objects with minimal fields.
    """
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FormRecordCell
        fields = ['id', 'content', 'create_date']

    def to_representation(self, instance: FormRecordCell) -> Dict[str, Any]:
        """
        Converts ObjectId to string for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        return data

class UploadFileSerializer(DocumentSerializer):
    """
    Serializer for UploadFile model, handling file uploads and metadata.
    """
    id = serializers.CharField(read_only=True)
    file_name = serializers.FileField()
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    form_structure = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all(), required=False, allow_null=True)

    class Meta:
        model = UploadFile
        fields = ['id', 'file_name', 'upload_date', 'user', 'form_structure']

    def to_representation(self, instance: UploadFile) -> Dict[str, Any]:
        """
        Converts ObjectId fields to strings and formats file URL and date.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        data['user'] = str(data['user']) if isinstance(data.get('user'), ObjectId) else data['user']
        data['form_structure'] = str(data['form_structure']) if isinstance(data.get('form_structure'), ObjectId) else data['form_structure']
        data['file_name'] = f'http://localhost:8000/{data["file_name"]}'
        data['date-fa'] = cvt_time(data['upload_date']) if data.get('upload_date') else None
        return data

    def create(self, validated_data: Dict[str, Any]) -> UploadFile:
        """
        Creates an UploadFile instance, saving the file to storage with a unique name.
        """
        try:
            file = validated_data.pop('file_name')
            file_name = f'uploads/{random.randint(0, 100000)}-{os.path.basename(file.name)}'
            file_path = default_storage.save(file_name, ContentFile(file.read()))
            validated_data['file_name'] = file_path
            upload_file = UploadFile(**validated_data)
            upload_file.save()
            logger.info("Created UploadFile with ID: %s, file: %s", upload_file.id, file_path)
            return upload_file
        except Exception as e:
            logger.error("Failed to create UploadFile: %s", str(e))
            raise serializers.ValidationError(f"Error saving file: {str(e)}")

    def update(self, instance: UploadFile, validated_data: Dict[str, Any]) -> UploadFile:
        """
        Updates an existing UploadFile instance, replacing the file if provided.
        """
        try:
            if 'file_name' in validated_data:
                file = validated_data.pop('file_name')
                file_name = f'uploads/{random.randint(0, 100000)}-{os.path.basename(file.name)}'
                file_path = default_storage.save(file_name, ContentFile(file.read()))
                # Delete old file if it exists
                if instance.file_name and default_storage.exists(instance.file_name):
                    default_storage.delete(instance.file_name)
                validated_data['file_name'] = file_path
            instance.file_name = validated_data.get('file_name', instance.file_name)
            instance.user = validated_data.get('user', instance.user)
            instance.form_structure = validated_data.get('form_structure', instance.form_structure)
            instance.save()
            logger.info("Updated UploadFile with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update UploadFile with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating file: {str(e)}")

    def delete(self, instance: UploadFile) -> None:
        """
        Deletes the UploadFile instance and its associated file from storage.
        """
        try:
            if instance.file_name and default_storage.exists(instance.file_name):
                default_storage.delete(instance.file_name)
            instance.delete()
            logger.info("Deleted UploadFile with ID: %s", instance.id)
        except Exception as e:
            logger.error("Failed to delete UploadFile with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error deleting file: {str(e)}")