import mongoengine as me
from mongoengine import fields
from datetime import datetime, timezone


class CustomUser(me.Document):
    """
    Represents a user in the system with authentication and role-based access control.
    """
    username = fields.StringField(max_length=150, required=True, unique=True)
    email = fields.StringField(max_length=254, required=False, unique=True, sparse=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    date_joined = fields.DateTimeField(default=lambda: datetime.now(timezone.utc))
    roles = fields.ListField(fields.StringField(max_length=50), default=list)

    def __str__(self):
        """Returns the username as the string representation."""
        return self.username

    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['username'], 'unique': True, 'name': 'unique_username_idx'},
            {'fields': ['email'], 'unique': True, 'sparse': True, 'name': 'unique_email_idx'}
        ],
        'ordering': ['-date_joined']
    }
