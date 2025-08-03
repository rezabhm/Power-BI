from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.form_handler.serializers import UploadFileSerializer, UploadExcelFileSerializer

upload_file_list_swagger = swagger_auto_schema(
    operation_summary='List Uploaded Files',
    operation_description=(
        'Allows authenticated users to retrieve a list of their uploaded files. '
        'Returns details for each file, ordered by upload date (newest first).'
    ),
    tags=['form_handler.upload_file'],
    responses={
        200: UploadFileSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

upload_file_create_swagger = swagger_auto_schema(
    operation_summary='Upload and Process Excel File',
    operation_description=(
        'Allows authenticated users to upload an Excel file to create forms, records, and cells based on detected form structures. '
        'The file must match a known form structure. '
        'Returns a success message or error details if the file is invalid or processing fails.'
    ),
    tags=['form_handler.upload_file'],
    request_body=UploadExcelFileSerializer,
    responses={
        200: openapi.Response(
            description='File upload completed successfully.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: 'Invalid file, duplicate file, or processing error.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'One or more form structures not found.'
    }
)