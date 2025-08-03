from typing import Dict, Any

from django.contrib.auth.models import User
from mongomock.object_id import ObjectId
from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer

from apps.core.documents import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'pk']


class CustomUserSerializer(DocumentSerializer):
    """
    Serializer for CustomUser model, handling user data serialization and deserialization.
    """
    id = serializers.CharField(read_only=True)
    roles = serializers.ListField(child=serializers.CharField(max_length=50), required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'roles']

    def to_representation(self, instance: CustomUser) -> Dict[str, Any]:
        """
        Converts ObjectId fields to strings for JSON serialization.
        """
        data = super().to_representation(instance)
        data['id'] = str(data['id']) if isinstance(data.get('id'), ObjectId) else data['id']
        return data