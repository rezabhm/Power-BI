from datetime import datetime, timezone
import mongoengine as me
from mongoengine import fields

from apps.core.documents import CustomUser


class FolderType(me.Document):
    """
    Defines types for categorizing folders.
    """
    type_name = fields.StringField(max_length=50, required=True, unique=True)

    def __str__(self):
        """Returns the type_name as the string representation."""
        return self.type_name

    meta = {
        'collection': 'folder_types',
        'indexes': [
            {'fields': ['type_name'], 'unique': True, 'name': 'unique_type_name_idx'}
        ]
    }

class Folder(me.Document):
    """
    Represents a folder for organizing form structures, owned by a user and categorized by type.
    """
    name = fields.StringField(max_length=50, required=True)
    create_date = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    folder_owner = fields.ReferenceField(CustomUser, required=True, reverse_delete_rule=me.CASCADE)
    folder_type = fields.ReferenceField(FolderType, required=True, reverse_delete_rule=me.CASCADE)

    def __str__(self):
        """Returns the folder name as the string representation."""
        return self.name

    meta = {
        'collection': 'folders',
        'indexes': [
            {'fields': ['folder_owner', 'name'], 'unique': True, 'name': 'unique_folder_owner_name_idx'},
            {'fields': ['folder_type']},
            {'fields': ['create_date']}
        ],
        'ordering': ['-create_date']
    }

class FormStructureColumn(me.EmbeddedDocument):
    """
    Embedded document representing a column in a form structure with metadata for data processing.
    """
    key_name = fields.StringField(max_length=50, required=True)
    title = fields.StringField(max_length=50, required=True)
    excel_column_name = fields.StringField(max_length=50, default='column')
    content_type = fields.StringField(max_length=20, default='str', choices=['str', 'int', 'bool', 'float', 'date'])

    def __str__(self):
        """Returns the column title as the string representation."""
        return self.title

class FormStructureSpecifications(me.EmbeddedDocument):
    """
    Embedded document for additional specifications of a form structure.
    """
    name = fields.StringField(max_length=50, required=True)
    content = fields.StringField(max_length=50, required=True)

    def __str__(self):
        """Returns the specification name as the string representation."""
        return self.name

class FormStructure(me.Document):
    """
    Represents the structure of a form, including columns and specifications, linked to a folder.
    """
    structure_name = fields.StringField(max_length=50, required=True)
    create_date = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    folder = fields.ReferenceField(Folder, required=True, reverse_delete_rule=me.CASCADE)
    record_num = fields.IntField(default=0, min_value=0)
    columns = fields.ListField(fields.EmbeddedDocumentField(FormStructureColumn), default=list)
    specifications = fields.ListField(fields.EmbeddedDocumentField(FormStructureSpecifications), default=list)

    def __str__(self):
        """Returns the structure name as the string representation."""
        return self.structure_name

    meta = {
        'collection': 'form_structures',
        'indexes': [
            {'fields': ['folder', 'structure_name'], 'unique': True, 'name': 'unique_folder_structure_idx'},
            {'fields': ['create_date']}
        ],
        'ordering': ['-create_date']
    }

class Form(me.Document):
    """
    Represents a form instance linked to a form structure and created by a user.
    """
    form_structure = fields.ReferenceField(FormStructure, required=True, reverse_delete_rule=me.CASCADE)
    user = fields.ReferenceField(CustomUser, required=True, reverse_delete_rule=me.CASCADE)
    create_date = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    form_name = fields.StringField(max_length=150, default='file')

    def __str__(self):
        """Returns the form ID as the string representation."""
        return str(self.id)

    meta = {
        'collection': 'forms',
        'indexes': [
            {'fields': ['form_structure', 'user']},
            {'fields': ['create_date']}
        ],
        'ordering': ['-create_date']
    }

class FormRecord(me.Document):
    """
    Represents a single record within a form, created by a user.
    """
    form = fields.ReferenceField(Form, required=True, reverse_delete_rule=me.CASCADE)
    create_date = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    user = fields.ReferenceField(CustomUser, required=True, reverse_delete_rule=me.CASCADE)

    def __str__(self):
        """Returns the record ID as the string representation."""
        return str(self.id)

    meta = {
        'collection': 'form_records',
        'indexes': [
            {'fields': ['form', 'user']},
            {'fields': ['create_date']}
        ],
        'ordering': ['-create_date']
    }

class FormRecordCell(me.Document):
    """
    Represents a single cell within a form record, linked to a form structure column.
    """
    form_record = fields.ReferenceField(FormRecord, required=True, reverse_delete_rule=me.CASCADE)
    form_structure = fields.ReferenceField(FormStructure, required=True, reverse_delete_rule=me.CASCADE)
    form_structure_column = fields.StringField(max_length=50, required=True)
    create_date = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    user = fields.ReferenceField(CustomUser, required=True, reverse_delete_rule=me.CASCADE)
    content = fields.StringField(max_length=250, required=True)

    def __str__(self):
        """Returns the cell ID as the string representation."""
        return str(self.id)

    meta = {
        'collection': 'form_record_cells',
        'indexes': [
            {'fields': ['form_record', 'form_structure_column']},
            {'fields': ['form_structure']},
            {'fields': ['user']},
            {'fields': ['create_date']}
        ],
        'ordering': ['-create_date']
    }

class UploadFile(me.Document):
    """
    Represents an uploaded file associated with a form structure and user, with automatic expiration.
    """
    file_name = fields.StringField(max_length=150, required=True)
    upload_date = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    user = fields.ReferenceField(CustomUser, required=True, reverse_delete_rule=me.CASCADE)
    form_structure = fields.ReferenceField(FormStructure, required=False, reverse_delete_rule=me.NULLIFY)

    def __str__(self):
        """Returns the file name as the string representation."""
        return self.file_name

    meta = {
        'collection': 'upload_files',
        'indexes': [
            {'fields': ['user', 'file_name'], 'unique': True, 'name': 'unique_user_file_idx'},
            {'fields': ['form_structure']},
            {'fields': ['upload_date'], 'expireAfterSeconds': 30 * 24 * 60 * 60}
        ],
        'ordering': ['-upload_date']
    }