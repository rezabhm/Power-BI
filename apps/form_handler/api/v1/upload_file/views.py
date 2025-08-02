from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.form_handler.serializers import *
from apps.form_handler.utils.detectFormStructure import detect_form_structure


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Upload an excel file to create forms and records',
    tags=['form_handler.upload_file'],
    manual_parameters=[
        openapi.Parameter(
            'file',
            openapi.IN_FORM,
            description="Excel file to upload",
            type=openapi.TYPE_FILE,
            required=True
        )
    ],
    responses={
        200: openapi.Response('File uploaded successfully', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
        )),
        400: 'Bad request (e.g., no file, invalid file, duplicate file)'
    },
    consumes=['multipart/form-data']
))
@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='List all uploaded files for the current user',
    tags=['form_handler.upload_file'],
    responses={200: UploadFileSerializer(many=True)}
))
class UploadFileViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
):
    """
    ViewSet for UploadFile operations
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UploadFileSerializer
    queryset = UploadFile.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return UploadFile.objects.filter(user=self.request.user).order_by('-upload_date')

    def create(self, request, *args, **kwargs):
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({'message': 'فایلی ارسال نشده است'}, status=status.HTTP_400_BAD_REQUEST)

        # Read Excel file
        try:
            file = pd.read_excel(excel_file)
        except Exception as e:
            return Response({'message': f'خطا در خواندن فایل: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Detect form structures
        form_structure_ids = detect_form_structure(file)
        try:
            form_structure_list = [FormStructure.objects.get(id=form_id) for form_id in form_structure_ids]
        except FormStructure.DoesNotExist:
            return Response({'message': 'یکی از ساختارهای فرم یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

        file_data = file.values.tolist()
        file_header = file.columns.tolist()
        file_name = excel_file.name

        # Check for duplicate file
        if UploadFile.objects.filter(file_name__exact=file_name):
            return Response({'message': 'این فایل قبلاً ارسال شده است'}, status=status.HTTP_400_BAD_REQUEST)

        if not form_structure_list:
            return Response({'message': 'فایل ارسال‌شده با هیچ‌یک از فرم‌ها تطابق نداشت'}, status=status.HTTP_400_BAD_REQUEST)

        used_objects = []
        for form_structure in form_structure_list:
            # Create Form
            form_data = {
                'form_structure': form_structure,
                'form_name': file_name,
                'user': request.user,
            }
            form_serializer = FormSerializer(data=form_data)
            if not form_serializer.is_valid():
                for obj in used_objects:
                    obj.delete()
                return Response({'message': 'خطا در ایجاد فرم', 'errors': form_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            form = form_serializer.save()
            used_objects.append(form)

            # Process each record
            for record in file_data:
                # Create FormRecord
                form_record_data = {
                    'form': form,
                    'user': request.user,
                }
                form_record_serializer = FormRecordSerializer(data=form_record_data)
                if not form_record_serializer.is_valid():
                    for obj in used_objects:
                        obj.delete()
                    return Response({'message': 'خطا در ایجاد رکورد فرم', 'errors': form_record_serializer.errors},
                                    status=status.HTTP_400_BAD_REQUEST)
                form_record = form_record_serializer.save()
                used_objects.append(form_record)

                # Process each cell in the record
                for item_id, item in enumerate(record):
                    # Find matching FormStructureColumn by excel_column_name
                    form_structure_column = None
                    for column in form_structure.columns:
                        if column.excel_column_name == file_header[item_id]:
                            form_structure_column = column
                            break

                    if not form_structure_column:
                        for obj in used_objects:
                            obj.delete()
                        return Response(
                            {
                                'message': 'فایل ارسالی صحیح نیست. لطفاً اشکالات فایل را مطابق ساختار فرم انتخابی اصلاح کنید و دوباره ارسال کنید'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Create FormRecordCell
                    record_cell_data = {
                        'form_record': form_record,
                        'form_structure_column': form_structure,  # Reference to FormStructure
                        'user': request.user,
                        'content': str(item),
                    }
                    record_cell_serializer = FormRecordCellSerializer(data=record_cell_data)
                    if not record_cell_serializer.is_valid():
                        for obj in used_objects:
                            obj.delete()
                        return Response(
                            {'message': 'خطا در ایجاد سلول رکورد', 'errors': record_cell_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)
                    record_cell = record_cell_serializer.save()
                    used_objects.append(record_cell)

            # Save the uploaded file
            uploaded_file_data = {
                'file_name': excel_file,
                'user': request.user,
                'form_structure': form_structure,
            }
            uploaded_file_serializer = UploadFileSerializer(data=uploaded_file_data)
            if not uploaded_file_serializer.is_valid():
                for obj in used_objects:
                    obj.delete()
                return Response({'message': 'خطا در ذخیره فایل آپلودشده', 'errors': uploaded_file_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)
            uploaded_file = uploaded_file_serializer.save()
            used_objects.append(uploaded_file)

        return Response({'message': 'عملیات آپلود فایل با موفقیت صورت گرفت'}, status=status.HTTP_200_OK)