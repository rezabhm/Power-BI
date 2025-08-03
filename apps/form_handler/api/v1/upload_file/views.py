from django.utils.decorators import method_decorator
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from apps.form_handler.documents import UploadFile
from apps.form_handler.serializers import UploadFileSerializer
from apps.form_handler.api.v1.upload_file.utils import process_uploaded_file
from apps.form_handler.api.v1.upload_file.swagger_decorators import (
    upload_file_list_swagger,
    upload_file_create_swagger
)


@method_decorator(name='list', decorator=upload_file_list_swagger)
@method_decorator(name='create', decorator=upload_file_create_swagger)
class UploadFileViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """
    ViewSet for handling file upload operations and listing uploaded files.
    Supports Excel file uploads to create forms, records, and cells based on detected form structures.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer
    queryset = UploadFile.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'id'

    def get_queryset(self):
        """
        Returns uploaded files for the authenticated user, ordered by upload date (newest first).
        """
        return self.queryset.filter(user=self.request.user).order_by('-upload_date')

    def create(self, request, *args, **kwargs):
        """
        Processes an uploaded Excel file to create forms, records, and cells based on detected form structures.
        Returns a success message or error details if validation or processing fails.
        """
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response(
                {'message': 'No file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = process_uploaded_file(excel_file, request.user)
        if isinstance(result, Response):
            return result
        return Response(
            {'message': 'File upload completed successfully.'},
            status=status.HTTP_200_OK
        )