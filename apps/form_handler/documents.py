import mongoengine as me
from datetime import datetime, timezone


# CustomUser mimicking Django's default User model with roles
class CustomUser(me.Document):
    username = me.StringField(max_length=150, unique=True, required=True)
    email = me.StringField(max_length=254, required=False)
    is_active = me.BooleanField(default=True)
    is_staff = me.BooleanField(default=False)
    is_superuser = me.BooleanField(default=False)
    date_joined = me.DateTimeField(default=lambda: datetime.now(timezone.utc))
    roles = me.ListField(me.StringField(), default=[])

    def __str__(self):
        return self.username

    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }


class FolderType(me.Document):
    type_name = me.StringField(max_length=50, required=True)

    def __str__(self):
        return self.type_name

    meta = {
        'collection': 'folder_types',
        'indexes': ['type_name']
    }


class Folder(me.Document):
    name = me.StringField(max_length=50, required=True)
    create_date = me.DateTimeField(default=lambda: datetime.now(timezone.utc))
    folder_owner = me.ReferenceField(CustomUser, required=True)
    folder_type = me.ReferenceField(FolderType, required=True)

    def __str__(self):
        return self.name

    meta = {
        'collection': 'folders',
        'indexes': ['folder_owner', 'folder_type', 'create_date']
    }


# Embedded Document for FormStructureColumn
class FormStructureColumn(me.EmbeddedDocument):
    key_name = me.StringField(max_length=50, required=True)
    title = me.StringField(max_length=50, required=True)
    excel_column_name = me.StringField(max_length=50, default='column')
    content_type = me.StringField(max_length=20, default='str', choices=['str', 'int', 'bool', 'float', 'date'])

    def __str__(self):
        return self.title


# Embedded Document for FormStructureSpecifications
class FormStructureSpecifications(me.EmbeddedDocument):
    name = me.StringField(max_length=50, required=True)
    content = me.StringField(max_length=50, required=True)

    def __str__(self):
        return self.name


class FormStructure(me.Document):
    structure_name = me.StringField(max_length=50, required=True)
    create_date = me.DateTimeField(default=lambda: datetime.now(timezone.utc))
    folder = me.ReferenceField(Folder, required=True)
    record_num = me.IntField(default=0)
    columns = me.ListField(me.EmbeddedDocumentField(FormStructureColumn), default=[])
    specifications = me.ListField(me.EmbeddedDocumentField(FormStructureSpecifications), default=[])

    def __str__(self):
        return self.structure_name

    meta = {
        'collection': 'form_structures',
        'indexes': ['folder', 'create_date']
    }


class Form(me.Document):
    form_structure = me.ReferenceField(FormStructure, required=True)
    user = me.ReferenceField(CustomUser, required=True)
    create_date = me.DateTimeField(default=lambda: datetime.now(timezone.utc))
    form_name = me.StringField(max_length=150, default='file')

    def __str__(self):
        return str(self.id)

    meta = {
        'collection': 'forms',
        'indexes': ['form_structure', 'user', 'create_date']
    }


class FormRecord(me.Document):
    form = me.ReferenceField(Form, required=True)
    create_date = me.DateTimeField(default=lambda: datetime.now(timezone.utc))
    user = me.ReferenceField(CustomUser, required=True)

    def __str__(self):
        return str(self.id)

    meta = {
        'collection': 'form_records',
        'indexes': ['form', 'user', 'create_date']
    }


class FormRecordCell(me.Document):
    form_record = me.ReferenceField(FormRecord, required=True)
    form_structure_column = me.ReferenceField(FormStructure, required=True)  # Reference to FormStructure
    create_date = me.DateTimeField(default=lambda: datetime.now(timezone.utc))
    user = me.ReferenceField(CustomUser, required=True)
    content = me.StringField(max_length=250, required=True)

    def __str__(self):
        return str(self.id)

    meta = {
        'collection': 'form_record_cells',
        'indexes': ['form_record', 'form_structure_column', 'user', 'create_date']
    }


class UploadFile(me.Document):
    file_name = me.StringField(max_length=150, required=True)
    upload_date = me.DateTimeField(default=lambda: datetime.now(timezone.utc))
    user = me.ReferenceField(CustomUser, required=True)
    form_structure = me.ReferenceField(FormStructure, default=None)

    def __str__(self):
        return self.file_name

    meta = {
        'collection': 'upload_files',
        'indexes': [
            {'fields': ['user']},
            {'fields': ['form_structure']},
            {'fields': ['upload_date'], 'expireAfterSeconds': 30 * 24 * 60 * 60}  # TTL index: expire after 30 days
        ]
    }
