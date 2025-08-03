from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from apps.form_handler.documents import Form
from apps.form_handler.serializers import FormSerializer
from apps.form_handler.api.v1.reporting.utils import (
    get_form_structure,
    generate_filter_config,
    apply_form_filters
)
from apps.form_handler.api.v1.reporting.swagger_decorators import (
    filter_config_list_swagger,
    form_structure_reporting_create_swagger
)

@method_decorator(name='list', decorator=filter_config_list_swagger)
class FilterConfigViewSet(GenericViewSet, mixins.ListModelMixin):
    """
    ViewSet for retrieving filter configuration for a specific FormStructure.
    Generates filter configurations based on column types (int, str, float).
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None  # Custom JSON response, no serializer needed

    def list(self, request, *args, **kwargs):
        """
        Retrieves filter configuration for a FormStructure specified by 'form-structure' query parameter.
        Returns configurations for each column based on its content type.
        """
        form_structure_id = request.query_params.get('form-structure')
        form_structure = get_form_structure(form_structure_id)
        if not form_structure:
            return Response(
                {'message': 'Invalid form structure ID provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        filter_config = generate_filter_config(form_structure)
        return Response({'filter-config': filter_config}, status=status.HTTP_200_OK)

@method_decorator(name='create', decorator=form_structure_reporting_create_swagger)
class FormStructureReportingViewSet(GenericViewSet, mixins.CreateModelMixin):
    """
    ViewSet for generating reports based on FormStructure and applied filters.
    Filters forms by date range and column-based conditions.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FormSerializer

    def create(self, request, *args, **kwargs):
        """
        Generates a report for forms associated with a FormStructure, filtered by date range and conditions.
        Returns serialized form data and aggregated row totals.
        """
        post_data = request.data
        form_structure_id = post_data.get('form-structure')
        form_structure = get_form_structure(form_structure_id)
        if not form_structure:
            return Response(
                {'message': 'Invalid form structure ID provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        filter_list = post_data.get('filter', [])
        if not filter_list:
            return Response(
                {'message': 'Filter list is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        form_list = Form.objects.filter(form_structure=form_structure)
        filtered_forms = apply_form_filters(form_list, filter_list, post_data)
        if isinstance(filtered_forms, Response):
            return filtered_forms

        form_serializer = self.get_serializer(filtered_forms, many=True, context={'filter': filter_list})
        row_total_list = [data.get('row_total_list', []) for data in form_serializer.data]

        return Response({
            'form-data': form_serializer.data,
            'form-structure-data': row_total_list
        }, status=status.HTTP_200_OK)