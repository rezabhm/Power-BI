from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, filters
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.models import CustomUser
from apps.core.serializers import CustomUserSerializer

# Swagger Decorators
admin_create_user_swagger = swagger_auto_schema(
    operation_summary='Create a New User (Admin)',
    operation_description=(
        'This endpoint allows administrators to create a new user. '
        'The request must include username, email, and other optional fields like first_name, last_name, and profile_image. '
        'The profile_image must be under 5MB. The response returns the created user’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    request_body=CustomUserSerializer,
    responses={
        201: CustomUserSerializer,
        400: 'Invalid input data (e.g., duplicate email or oversized profile image).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)

admin_retrieve_user_swagger = swagger_auto_schema(
    operation_summary='Retrieve a User (Admin)',
    operation_description=(
        'This endpoint retrieves the details of a specific user by their ID. '
        'The response includes all user fields. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    responses={
        200: CustomUserSerializer,
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'User not found.'
    }
)

admin_update_user_swagger = swagger_auto_schema(
    operation_summary='Update a User (Admin)',
    operation_description=(
        'This endpoint allows administrators to update the details of a specific user by their ID. '
        'All user fields can be updated. The profile_image must be under 5MB. '
        'The response returns the updated user’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    request_body=CustomUserSerializer,
    responses={
        200: CustomUserSerializer,
        400: 'Invalid input data (e.g., oversized profile image).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'User not found.'
    }
)

admin_partial_update_user_swagger = swagger_auto_schema(
    operation_summary='Partially Update a User (Admin)',
    operation_description=(
        'This endpoint allows administrators to partially update the details of a specific user by their ID. '
        'Any subset of user fields can be updated. The profile_image must be under 5MB. '
        'The response returns the updated user’s details. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    request_body=CustomUserSerializer,
    responses={
        200: CustomUserSerializer,
        400: 'Invalid input data (e.g., oversized profile image).',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'User not found.'
    }
)

admin_destroy_user_swagger = swagger_auto_schema(
    operation_summary='Delete a User (Admin)',
    operation_description=(
        'This endpoint allows administrators to delete a specific user by their ID. '
        'This operation is irreversible. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    responses={
        204: 'User deleted successfully.',
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.',
        404: 'User not found.'
    }
)

admin_list_user_swagger = swagger_auto_schema(
    operation_summary='List Users (Admin)',
    operation_description=(
        'This endpoint retrieves a list of all users. '
        'The response is paginated and can be filtered by username and email. '
        'This operation is restricted to admin users only and requires JWT authentication.'
    ),
    tags=['admin.core.user'],
    responses={
        200: CustomUserSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required for admin users.',
        403: 'Forbidden: User is not an admin.'
    }
)


@method_decorator(name='create', decorator=admin_create_user_swagger)
@method_decorator(name='retrieve', decorator=admin_retrieve_user_swagger)
@method_decorator(name='update', decorator=admin_update_user_swagger)
@method_decorator(name='partial_update', decorator=admin_partial_update_user_swagger)
@method_decorator(name='destroy', decorator=admin_destroy_user_swagger)
@method_decorator(name='list', decorator=admin_list_user_swagger)
class CustomUserAdminAPIView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
):
    """
    Admin-only API ViewSet for managing CustomUser records.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = CustomUserSerializer
    lookup_field = 'id'
    queryset = CustomUser.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
