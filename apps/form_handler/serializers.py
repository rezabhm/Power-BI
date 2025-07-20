import os
import random
from bson import ObjectId
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework_mongoengine.serializers import DocumentSerializer
from rest_framework import serializers
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
from apps.form_handler.utils.time_handler import cvt_time


class CustomUserSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)
    roles = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'roles']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data

class FolderTypeSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FolderType
        fields = ['id', 'type_name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data

class FolderTypeListSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FolderType
        fields = ['id', 'type_name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data

class FolderSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)
    folder_owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    folder_type = serializers.PrimaryKeyRelatedField(queryset=FolderType.objects.all())

    class Meta:
        model = Folder
        fields = ['id', 'name', 'create_date', 'folder_owner', 'folder_type']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        if isinstance(data.get('folder_owner'), ObjectId):
            data['folder_owner'] = str(data['folder_owner'])
        if isinstance(data.get('folder_type'), ObjectId):
            data['folder_type'] = str(data['folder_type'])
        return data

class FolderListSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'create_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data

class FormStructureColumnSerializer(serializers.Serializer):
    key_name = serializers.CharField(max_length=50, required=True)
    title = serializers.CharField(max_length=50, required=True)
    excel_column_name = serializers.CharField(max_length=50, required=False, default='column')
    content_type = serializers.ChoiceField(choices=['str', 'int', 'bool', 'float', 'date'], default='str')

    def create(self, validated_data):
        return FormStructureColumn(**validated_data)

    def update(self, instance, validated_data):
        instance.key_name = validated_data.get('key_name', instance.key_name)
        instance.title = validated_data.get('title', instance.title)
        instance.excel_column_name = validated_data.get('excel_column_name', instance.excel_column_name)
        instance.content_type = validated_data.get('content_type', instance.content_type)
        return instance

class FormStructureColumnListSerializer(serializers.ListSerializer):
    child = FormStructureColumnSerializer()

class FormStructureSpecificationsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=True)
    content = serializers.CharField(max_length=50, required=True)

    def create(self, validated_data):
        return FormStructureSpecifications(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.content = validated_data.get('content', instance.content)
        return instance

class FormStructureSpecificationsListSerializer(serializers.ListSerializer):
    child = FormStructureSpecificationsSerializer()

class FormStructureSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
    columns = FormStructureColumnSerializer(many=True, required=False)
    specifications = FormStructureSpecificationsSerializer(many=True, required=False)

    class Meta:
        model = FormStructure
        fields = ['id', 'structure_name', 'create_date', 'folder', 'record_num', 'columns', 'specifications']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        if isinstance(data.get('folder'), ObjectId):
            data['folder'] = str(data['folder'])
        return data

    def create(self, validated_data):
        columns_data = validated_data.pop('columns', [])
        specifications_data = validated_data.pop('specifications', [])
        form_structure = FormStructure(**validated_data)
        form_structure.columns = [FormStructureColumn(**column) for column in columns_data]
        form_structure.specifications = [FormStructureSpecifications(**spec) for spec in specifications_data]
        form_structure.save()
        return form_structure

    def update(self, instance, validated_data):
        instance.structure_name = validated_data.get('structure_name', instance.structure_name)
        instance.folder = validated_data.get('folder', instance.folder)
        instance.record_num = validated_data.get('record_num', instance.record_num)
        if 'columns' in validated_data:
            instance.columns = [FormStructureColumn(**column) for column in validated_data['columns']]
        if 'specifications' in validated_data:
            instance.specifications = [FormStructureSpecifications(**spec) for spec in validated_data['specifications']]
        instance.save()
        return instance


class FormStructureListSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FormStructure
        fields = ['id', 'structure_name', 'create_date', 'record_num']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data


class FormSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)
    form_structure = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = Form
        fields = ['id', 'form_structure', 'user', 'create_date', 'form_name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        if isinstance(data.get('form_structure'), ObjectId):
            data['form_structure'] = str(data['form_structure'])
        if isinstance(data.get('user'), User):
            data['user'] = str(data['user'])
        return data


class FormListSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'form_name', 'create_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data


class FormRecordSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)
    form = serializers.PrimaryKeyRelatedField(queryset=Form.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = FormRecord
        fields = ['id', 'form', 'create_date', 'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        if isinstance(data.get('form'), ObjectId):
            data['form'] = str(data['form'])
        if isinstance(data.get('user'), ObjectId):
            data['user'] = str(data['user'])
        return data


class FormRecordListSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FormRecord
        fields = ['id', 'create_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data


class FormRecordCellSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)
    form_record = serializers.PrimaryKeyRelatedField(queryset=FormRecord.objects.all())
    form_structure_column = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = FormRecordCell
        fields = ['id', 'form_record', 'form_structure_column', 'create_date', 'user', 'content']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        if isinstance(data.get('form_record'), ObjectId):
            data['form_record'] = str(data['form_record'])
        if isinstance(data.get('form_structure_column'), ObjectId):
            data['form_structure_column'] = str(data['form_structure_column'])
        if isinstance(data.get('user'), ObjectId):
            data['user'] = str(data['user'])
        return data


class FormRecordCellListSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = FormRecordCell
        fields = ['id', 'content', 'create_date']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        return data



class UploadFileSerializer(DocumentSerializer):
    id = serializers.CharField(read_only=True)
    file_name = serializers.FileField()
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    form_structure = serializers.PrimaryKeyRelatedField(queryset=FormStructure.objects.all(), required=False)

    class Meta:
        model = UploadFile
        fields = ['id', 'file_name', 'upload_date', 'user', 'form_structure']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(data.get('id'), ObjectId):
            data['id'] = str(data['id'])
        if isinstance(data.get('user'), ObjectId):
            data['user'] = str(data['user'])
        if isinstance(data.get('form_structure'), ObjectId):
            data['form_structure'] = str(data['form_structure'])
        data['file_name'] = f'http://localhost:8000/{data["file_name"]}'
        data['date-fa'] = cvt_time(data['upload_date'])
        return data

    def create(self, validated_data):
        file = validated_data.pop('file_name')
        file_name = f'uploads/{str(random.randint(0,100000))}-{os.path.basename(file.name)}'
        file_path = default_storage.save(file_name, ContentFile(file.read()))
        validated_data['file_name'] = file_path
        upload_file = UploadFile(**validated_data)
        upload_file.save()
        return upload_file

    def update(self, instance, validated_data):
        if 'file_name' in validated_data:
            file = validated_data.pop('file_name')
            file_name = f'uploads/{str(random.randint(0,100000))}-{os.path.basename(file.name)}'
            file_path = default_storage.save(file_name, ContentFile(file.read()))
            validated_data['file_name'] = file_path
        instance.file_name = validated_data.get('file_name', instance.file_name)
        instance.user = validated_data.get('user', instance.user)
        instance.form_structure = validated_data.get('form_structure', instance.form_structure)
        instance.save()
        return instance

    def delete(self, instance):
        if instance.file_name and default_storage.exists(instance.file_name):
            default_storage.delete(instance.file_name)
        instance.delete()
        return instance
