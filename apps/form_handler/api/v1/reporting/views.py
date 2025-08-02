from collections import Counter

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.form_handler.documents import FormStructure, Form, FormRecord, FormRecordCell
from apps.form_handler.serializers import FormSerializer
from apps.form_handler.utils.time_handler import jalali_to_gregorian


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_summary='Get filter configuration for a form structure',
    tags=['form_handler.reporting'],
    manual_parameters=[
        openapi.Parameter('form-structure', openapi.IN_QUERY, description="ID of the form structure",
                          type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Response('Filter configuration', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'filter-config': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['int', 'str', 'float']),
                            'key_name': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'column_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'condition_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                             enum=['gte', 'lte', 'gt', 'lt']),
                            'condition_int': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'content_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                           items=openapi.Schema(type=openapi.TYPE_STRING))
                        }
                    )
                )
            }
        )),
        400: 'Invalid form structure ID'
    }
))
class FilterConfigViewSet(GenericViewSet, mixins.ListModelMixin):
    """
    ViewSet for retrieving filter configuration for a FormStructure
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None  # No serializer needed as we return custom JSON

    def list(self, request, *args, **kwargs):
        try:
            form_structure = FormStructure.objects.get(id=request.query_params.get('form-structure'))
        except FormStructure.DoesNotExist:
            return Response({'message': 'آیدی ساختار فرم اشتباه میباشد'}, status=status.HTTP_400_BAD_REQUEST)

        filter_config = []
        for column_index, column in enumerate(form_structure.columns):
            if column.content_type == 'int':
                config = {
                    'type': 'int',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': column_index,  # Use index instead of pk
                    'condition_type': 'gte',
                    'condition_int': 0
                }
                config2 = {
                    'type': 'int',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': column_index,
                    'condition_type': 'lte',
                    'condition_int': 0
                }
                filter_config.append(config)
                filter_config.append(config2)

            elif column.content_type == 'str':
                form_cells = FormRecordCell.objects.filter(form_structure_column=form_structure)
                content_list = [cell.content for cell in form_cells]
                content_counter = Counter(content_list)
                content_list = list(content_counter.keys())

                config = {
                    'type': 'str',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': column_index,
                    'content_list': content_list,
                }
                filter_config.append(config)

            elif column.content_type == 'float':
                config = {
                    'type': 'float',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': column_index,
                    'condition_type': 'gte',
                    'condition_int': 0
                }
                config2 = {
                    'type': 'float',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': column_index,
                    'condition_type': 'lte',
                    'condition_int': 0
                }
                filter_config.append(config)
                filter_config.append(config2)

        return Response({'filter-config': filter_config}, status=status.HTTP_200_OK)


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_summary='Generate a report based on a form structure and filters',
    tags=['form_handler.reporting'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'form-structure': openapi.Schema(type=openapi.TYPE_STRING, description='ID of the form structure'),
            'data-from': openapi.Schema(type=openapi.TYPE_STRING, description='Start date (Jalali)'),
            'data-to': openapi.Schema(type=openapi.TYPE_STRING, description='End date (Jalali)'),
            'filter': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['int', 'str', 'float']),
                        'key_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'condition_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['gte', 'lte', 'gt', 'lt']),
                        'condition_int': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'condition_str_list': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                               items=openapi.Schema(type=openapi.TYPE_STRING))
                    }
                )
            )
        },
        required=['form-structure', 'filter']
    ),
    responses={
        200: openapi.Response('Report data', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'form-data': FormSerializer(many=True),
                'form-structure-data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            }
        )),
        400: 'Invalid input data'
    }
))
class FormStructureReportingViewSet(GenericViewSet, mixins.CreateModelMixin):
    """
    ViewSet for generating reports based on FormStructure and filters
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormSerializer

    def create(self, request, *args, **kwargs):
        post_data = request.data

        try:
            form_structure = FormStructure.objects.get(id=post_data.get('form-structure'))
        except FormStructure.DoesNotExist:
            return Response({'message': 'آیدی ساختار فرم اشتباه میباشد'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            filter_list = post_data.get('filter')
        except:
            return Response({'message': 'فیلترها ارسال نشده است'}, status=status.HTTP_400_BAD_REQUEST)

        form_list = Form.objects.filter(form_structure=form_structure)

        if post_data.get('data-from'):
            try:
                form_list = form_list.filter(create_date__gte=jalali_to_gregorian(post_data.get('data-from')))
            except:
                return Response({'message': 'فرمت تاریخ شروع اشتباه است'}, status=status.HTTP_400_BAD_REQUEST)

        if post_data.get('data-to'):
            try:
                form_list = form_list.filter(create_date__lte=jalali_to_gregorian(post_data.get('data-to')))
            except:
                return Response({'message': 'فرمت تاریخ پایان اشتباه است'}, status=status.HTTP_400_BAD_REQUEST)

        for flt in filter_list:
            if flt['type'] == 'int' and float(flt.get('condition_int', 0)) > 0:
                new_list = []
                for form in form_list:
                    form_records = FormRecord.objects.filter(form=form)
                    x = 0
                    for record in form_records:
                        form_cell_list = FormRecordCell.objects.filter(
                            form_record=record,
                            form_structure_column=form_structure
                        )
                        for cell in form_cell_list:
                            for column in form_structure.columns:
                                if column.key_name == flt['key_name'] and column.content_type == 'int':
                                    try:
                                        x += int(cell.content)
                                    except (ValueError, TypeError):
                                        pass
                    y = float(flt['condition_int'])
                    if flt['condition_type'] == 'gt' and x > y:
                        new_list.append(form)
                    elif flt['condition_type'] == 'gte' and x >= y:
                        new_list.append(form)
                    elif flt['condition_type'] == 'lt' and x < y:
                        new_list.append(form)
                    elif flt['condition_type'] == 'lte' and x <= y:
                        new_list.append(form)
                form_list = new_list

            elif flt['type'] == 'float' and float(flt.get('condition_int', 0)) > 0:
                new_list = []
                for form in form_list:
                    form_records = FormRecord.objects.filter(form=form)
                    x = 0.0
                    for record in form_records:
                        form_cell_list = FormRecordCell.objects.filter(
                            form_record=record,
                            form_structure_column=form_structure
                        )
                        for cell in form_cell_list:
                            for column in form_structure.columns:
                                if column.key_name == flt['key_name'] and column.content_type == 'float':
                                    try:
                                        x += float(cell.content)
                                    except (ValueError, TypeError):
                                        pass
                    y = float(flt['condition_int'])
                    if flt['condition_type'] == 'gt' and x > y:
                        new_list.append(form)
                    elif flt['condition_type'] == 'gte' and x >= y:
                        new_list.append(form)
                    elif flt['condition_type'] == 'lt' and x < y:
                        new_list.append(form)
                    elif flt['condition_type'] == 'lte' and x <= y:
                        new_list.append(form)
                form_list = new_list

            elif flt['type'] == 'str' and flt.get('condition_str_list', []):
                new_list = []
                for form in form_list:
                    form_records = FormRecord.objects.filter(form=form)
                    for record in form_records:
                        form_cell_list = FormRecordCell.objects.filter(
                            form_record=record,
                            form_structure_column=form_structure
                        )
                        for cell in form_cell_list:
                            for column in form_structure.columns:
                                if column.key_name == flt['key_name'] and column.content_type == 'str':
                                    if cell.content in flt['condition_str_list']:
                                        new_list.append(form)
                                        break
                            if form in new_list:
                                break
                form_list = new_list

        form_serializer = self.get_serializer(form_list, many=True, context={'filter': filter_list})
        row_total_list = [data.get('row_total_list', []) for data in form_serializer.data]

        return Response({
            'form-data': form_serializer.data,
            'form-structure-data': row_total_list
        }, status=status.HTTP_200_OK)