import os
import random
from typing import Any, Dict
from bson import ObjectId
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework import serializers
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

# Configure logger for consistent logging across the module
logger = logging.getLogger(__name__)


class BaseSerializer(serializers.Serializer):
    """Base serializer with common functionality for MongoDB ObjectId conversion."""

    def _convert_objectid_to_str(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId fields to strings for JSON serialization."""
        for field in data:
            if isinstance(data[field], ObjectId):
                data[field] = str(data[field])
        return data


class FolderTypeSerializer(BaseSerializer):
    """Serializer for FolderType model to handle folder type creation and updates."""

    id = serializers.CharField(read_only=True)
    type_name = serializers.CharField(max_length=50, required=True)

    def create(self, validated_data: Dict[str, Any]) -> FolderType:
        """Create a new FolderType instance and save it to the database."""
        try:
            folder_type = FolderType(**validated_data)
            folder_type.save()
            logger.info("Created FolderType with ID: %s", folder_type.id)
            return folder_type
        except Exception as e:
            logger.error("Failed to create FolderType: %s", str(e))
            raise serializers.ValidationError(f"Error creating FolderType: {str(e)}")

    def update(self, instance: FolderType, validated_data: Dict[str, Any]) -> FolderType:
        """Update an existing FolderType instance with validated data."""
        try:
            instance.type_name = validated_data.get('type_name', instance.type_name)
            instance.save()
            logger.info("Updated FolderType with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update FolderType with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating FolderType: {str(e)}")

    def to_representation(self, instance: FolderType) -> Dict[str, Any]:
        """Convert FolderType instance to JSON-serializable representation."""
        data = super().to_representation(instance)
        return self._convert_objectid_to_str(data)


class FolderTypeListSerializer(FolderTypeSerializer):
    """Serializer for listing FolderType objects, inheriting from FolderTypeSerializer."""
    pass


class FolderSerializer(BaseSerializer):
    """Serializer for Folder model to manage folder creation and updates."""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=50, required=True)
    create_date = serializers.DateTimeField(read_only=True)
    folder_owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    folder_type = serializers.PrimaryKeyRelatedField(queryset=FolderType.objects.all())

    def create(self, validated_data: Dict[str, Any]) -> Folder:
        """Create a new Folder instance and save it to the database."""
        try:
            folder = Folder(**validated_data)
            folder.save()
            logger.info("Created Folder with ID: %s", folder.id)
            return folder
        except Exception as e:
            logger.error("Failed to create Folder: %s", str(e))
            raise serializers.ValidationError(f"Error creating Folder: {str(e)}")

    def update(self, instance: Folder, validated_data: Dict[str, Any]) -> Folder:
        """Update an existing Folder instance with validated data."""
        try:
            instance.name = validated_data.get('name', instance.name)
            instance.folder_owner = validated_data.get('folder_owner', instance.folder_owner)
            instance.folder_type = validated_data.get('folder_type', instance.folder_type)
            instance.save()
            logger.info("Updated Folder with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update Folder with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating Folder: {str(e)}")

    def to_representation(self, instance: Folder) -> Dict[str, Any]:
        """Convert Folder instance to JSON-serializable representation."""
        data = super().to_representation(instance)
        data = self._convert_objectid_to_str(data)
        data['folder_owner'] = str(data['folder_owner'])
        data['folder_type'] = str(data['folder_type'])
        return data


class FolderListSerializer(FolderSerializer):
    """Serializer for listing Folder objects with minimal fields."""
    pass


class FormStructureColumnSerializer(BaseSerializer):
    """Serializer for FormStructureColumn embedded document."""

    key_name = serializers.CharField(max_length=50, required=True)
    title = serializers.CharField(max_length=50, required=True)
    excel_column_name = serializers.CharField(max_length=50, required=False, default='column')
    content_type = serializers.ChoiceField(choices=['str', 'int', 'bool', 'float', 'date'], default='str')

    def create(self, validated_data: Dict[str, Any]) -> FormStructureColumn:
        """Create a new FormStructureColumn instance."""
        return FormStructureColumn(**validated_data)

    def update(self, instance: FormStructureColumn, validated_data: Dict[str, Any]) -> FormStructureColumn:
        """Update an existing FormStructureColumn instance with validated data."""
        instance.key_name = validated_data.get('key_name', instance.key_name)
        instance.title = validated_data.get('title', instance.title)
        instance.excel_column_name = validated_data.get('excel_column_name', instance.excel_column_name)
        instance.content_type = validated_data.get('content_type', instance.content_type)
        return instance


class FormStructureColumnListSerializer(serializers.ListSerializer):
    """List serializer for FormStructureColumn objects."""
    child = FormStructureColumnSerializer()


class FormStructureSpecificationsSerializer(BaseSerializer):
    """Serializer for FormStructureSpecifications embedded document."""

    name = serializers.CharField(max_length=50, required=True)
    content = serializers.CharField(max_length=50, required=True)

    def create(self, validated_data: Dict[str, Any]) -> FormStructureSpecifications:
        """Create a new FormStructureSpecifications instance."""
        return FormStructureSpecifications(**validated_data)

    def update(self, instance: FormStructureSpecifications,
               validated_data: Dict[str, Any]) -> FormStructureSpecifications:
        """Update an existing FormStructureSpecifications instance with validated data."""
        instance.name = validated_data.get('name', instance.name)
        instance.content = validated_data.get('content', instance.content)
        return instance


class FormStructureSpecificationsListSerializer(serializers.ListSerializer):
    """List serializer for FormStructureSpecifications objects."""
    child = FormStructureSpecificationsSerializer()


class FormStructureSerializer(BaseSerializer):
    """Serializer for FormStructure model to manage form structure creation and updates."""

    id = serializers.CharField(read_only=True)
    structure_name = serializers.CharField(max_length=50, required=True)
    create_date = serializers.DateTimeField(read_only=True)
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
    record_num = serializers.IntegerField(default=0, min_value=0)
    columns = FormStructureColumnSerializer(many=True, required=False)
    specifications = FormStructureSpecificationsSerializer(many=True, required=False)

    def create(self, validated_data: Dict[str, Any]) -> FormStructure:
        """Create a new FormStructure instance with embedded columns and specifications."""
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
        """Update an existing FormStructure instance with validated data."""
        try:
            instance.structure_name = validated_data.get('structure_name', instance.structure_name)
            instance.folder = validated_data.get('folder', instance.folder)
            instance.record_num = validated_data.get('record_num', instance.record_num)
            if 'columns' in validated_data:
                instance.columns = [FormStructureColumn(**column) for column in validated_data['columns']]
            if 'specifications' in validated_data:
                instance.specifications = [FormStructureSpecifications(**spec) for spec in
                                           validated_data['specifications']]
            instance.save()
            logger.info("Updated FormStructure with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update FormStructure with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating FormStructure: {str(e)}")

    def to_representation(self, instance: FormStructure) -> Dict[str, Any]:
        """Convert FormStructure instance to JSON-serializable representation."""
        data = super().to_representation(instance)
        data = self._convert_objectid_to_str(data)
        data['folder'] = str(data['folder'])
        return data


class FormStructureListSerializer(FormStructureSerializer):
    """Serializer for listing FormStructure objects with minimal fields."""
    pass


class FormSerializer(BaseSerializer):
    """Serializer for Form model to manage form creation and updates."""

    id = serializers.CharField(read_only=True)
    form_structure = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    create_date = serializers.DateTimeField(read_only=True)
    form_name = serializers.CharField(max_length=150, default='file')

    def create(self, validated_data: Dict[str, Any]) -> Form:
        """Create a new Form instance and save it to the database."""
        try:
            form = Form(**validated_data)
            form.save()
            logger.info("Created Form with ID: %s", form.id)
            return form
        except Exception as e:
            logger.error("Failed to create Form: %s", str(e))
            raise serializers.ValidationError(f"Error creating Form: {str(e)}")

    def update(self, instance: Form, validated_data: Dict[str, Any]) -> Form:
        """Update an existing Form instance with validated data."""
        try:
            instance.form_structure = validated_data.get('form_structure', instance.form_structure)
            instance.user = validated_data.get('user', instance.user)
            instance.form_name = validated_data.get('form_name', instance.form_name)
            instance.save()
            logger.info("Updated Form with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update Form with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating Form: {str(e)}")

    def to_representation(self, instance: Form) -> Dict[str, Any]:
        """Convert Form instance to JSON-serializable representation."""
        data = super().to_representation(instance)
        data = self._convert_objectid_to_str(data)
        data['form_structure'] = str(data['form_structure'])
        data['user'] = str(data['user'])
        return data


class FormListSerializer(FormSerializer):
    """Serializer for listing Form objects with minimal fields."""
    pass


class FormRecordSerializer(BaseSerializer):
    """Serializer for FormRecord model to manage form record creation and updates."""

    id = serializers.CharField(read_only=True)
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())
    create_date = serializers.DateTimeField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    def create(self, validated_data: Dict[str, Any]) -> FormRecord:
        """Create a new FormRecord instance and save it to the database."""
        try:
            form_record = FormRecord(**validated_data)
            form_record.save()
            logger.info("Created FormRecord with ID: %s", form_record.id)
            return form_record
        except Exception as e:
            logger.error("Failed to create FormRecord: %s", str(e))
            raise serializers.ValidationError(f"Error creating FormRecord: {str(e)}")

    def update(self, instance: FormRecord, validated_data: Dict[str, Any]) -> FormRecord:
        """Update an existing FormRecord instance with validated data."""
        try:
            instance.form = validated_data.get('form', instance.form)
            instance.user = validated_data.get('user', instance.user)
            instance.save()
            logger.info("Updated FormRecord with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update FormRecord with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating FormRecord: {str(e)}")

    def to_representation(self, instance: FormRecord) -> Dict[str, Any]:
        """Convert FormRecord instance to JSON-serializable representation."""
        data = super().to_representation(instance)
        data = self._convert_objectid_to_str(data)
        data['form'] = str(data['form'])
        data['user'] = str(data['user'])
        return data


class FormRecordListSerializer(FormRecordSerializer):
    """Serializer for listing FormRecord objects with minimal fields."""
    pass


class FormRecordCellSerializer(BaseSerializer):
    """Serializer for FormRecordCell model to manage form record cell creation and updates."""

    id = serializers.CharField(read_only=True)
    form_record = serializers.PrimaryKeyRelatedField(queryset=FormRecord.objects.all())
    form_structure = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all())
    form_structure_column = serializers.CharField(max_length=50)
    create_date = serializers.DateTimeField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    content = serializers.CharField(max_length=250)

    def create(self, validated_data: Dict[str, Any]) -> FormRecordCell:
        """Create a new FormRecordCell instance and save it to the database."""
        try:
            form_record_cell = FormRecordCell(**validated_data)
            form_record_cell.save()
            logger.info("Created FormRecordCell with ID: %s", form_record_cell.id)
            return form_record_cell
        except Exception as e:
            logger.error("Failed to create FormRecordCell: %s", str(e))
            raise serializers.ValidationError(f"Error creating FormRecordCell: {str(e)}")

    def update(self, instance: FormRecordCell, validated_data: Dict[str, Any]) -> FormRecordCell:
        """Update an existing FormRecordCell instance with validated data."""
        try:
            instance.form_record = validated_data.get('form_record', instance.form_record)
            instance.form_structure = validated_data.get('form_structure', instance.form_structure)
            instance.form_structure_column = validated_data.get('form_structure_column', instance.form_structure_column)
            instance.user = validated_data.get('user', instance.user)
            instance.content = validated_data.get('content', instance.content)
            instance.save()
            logger.info("Updated FormRecordCell with ID: %s", instance.id)
            return instance
        except Exception as e:
            logger.error("Failed to update FormRecordCell with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error updating FormRecordCell: {str(e)}")

    def to_representation(self, instance: FormRecordCell) -> Dict[str, Any]:
        """Convert FormRecordCell instance to JSON-serializable representation."""
        data = super().to_representation(instance)
        data = self._convert_objectid_to_str(data)
        data['form_record'] = str(data['form_record'])
        data['form_structure'] = str(data['form_structure'])
        data['user'] = str(data['user'])
        return data


class FormRecordCellListSerializer(FormRecordCellSerializer):
    """Serializer for listing FormRecordCell objects with minimal fields."""
    pass


class UploadFileSerializer(BaseSerializer):
    """Serializer for UploadFile model to manage file uploads and metadata."""

    id = serializers.CharField(read_only=True)
    file_name = serializers.FileField()
    upload_date = serializers.DateTimeField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    form_structure = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all(), required=False,
                                                        allow_null=True)

    def create(self, validated_data: Dict[str, Any]) -> UploadFile:
        """Create a new UploadFile instance, save the file, and store metadata."""
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
        """Update an existing UploadFile instance, replacing the file if provided."""
        try:
            if 'file_name' in validated_data:
                file = validated_data.pop('file_name')
                file_name = f'uploads/{random.randint(0, 100000)}-{os.path.basename(file.name)}'
                file_path = default_storage.save(file_name, ContentFile(file.read()))
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

    def to_representation(self, instance: UploadFile) -> Dict[str, Any]:
        """Convert UploadFile instance to JSON-serializable representation with file URL and formatted date."""
        data = super().to_representation(instance)
        data = self._convert_objectid_to_str(data)
        data['user'] = str(data['user'])
        data['form_structure'] = str(data['form_structure']) if data.get('form_structure') else None
        data['file_name'] = f'http://localhost:8000/{data["file_name"]}'
        data['date-fa'] = cvt_time(data['upload_date']) if data.get('upload_date') else None
        return data

    def delete(self, instance: UploadFile) -> None:
        """Delete an UploadFile instance and its associated file from storage."""
        try:
            if instance.file_name and default_storage.exists(instance.file_name):
                default_storage.delete(instance.file_name)
            instance.delete()
            logger.info("Deleted UploadFile with ID: %s", instance.id)
        except Exception as e:
            logger.error("Failed to delete UploadFile with ID %s: %s", instance.id, str(e))
            raise serializers.ValidationError(f"Error deleting file: {str(e)}")


class UploadExcelFileSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="Excel file to upload.")