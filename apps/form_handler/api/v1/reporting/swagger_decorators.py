from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.form_handler.serializers import FormSerializer

filter_config_list_swagger = swagger_auto_schema(
    operation_summary='Retrieve Filter Configuration for Form Structure',
    operation_description=(
        'Allows authenticated users to retrieve filter configurations for a specific form structure. '
        'The form-structure ID must be provided as a query parameter. '
        'Returns configurations for each column based on its type (int, str, float). '
        'For int and float types, includes gte and lte conditions. '
        'For str type, includes a list of unique content values.'
    ),
    tags=['form_handler.filter_config'],
    manual_parameters=[
        openapi.Parameter(
            'form-structure',
            openapi.IN_QUERY,
            description='Unique ID of the form structure to retrieve filter configurations for.',
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description='Filter configuration data.',
            schema=openapi.Schema(
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
                                'condition_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['gte', 'lte'], nullable=True),
                                'condition_int': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                                'content_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), nullable=True)
                            }
                        )
                    )
                }
            )
        ),
        400: 'Invalid form structure ID provided.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

form_structure_reporting_create_swagger = swagger_auto_schema(
    operation_summary='Generate Form Structure Report',
    operation_description=(
        'Allows authenticated users to generate a report for forms associated with a form structure. '
        'Requires form-structure ID and filter list in the request body. '
        'Optional date-from and date-to fields filter by creation date (Jalali format). '
        'Filters can include int/float conditions (gt, gte, lt, lte) or string matches. '
        'Returns serialized form data and aggregated row totals.'
    ),
    tags=['form_handler.reporting'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'form-structure': openapi.Schema(type=openapi.TYPE_INTEGER, description='Unique ID of the form structure.'),
            'filter': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['int', 'str', 'float']),
                        'key_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'condition_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['gt', 'gte', 'lt', 'lte'], nullable=True),
                        'condition_int': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                        'condition_str_list': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), nullable=True)
                    }
                )
            ),
            'data-from': openapi.Schema(type=openapi.TYPE_STRING, description='Start date in Jalali format (YYYY-MM-DD).', nullable=True),
            'data-to': openapi.Schema(type=openapi.TYPE_STRING, description='End date in Jalali format (YYYY-MM-DD).', nullable=True)
        },
        required=['form-structure', 'filter']
    ),
    responses={
        200: openapi.Response(
            description='Report data with serialized forms and row totals.',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'form-data': openapi.Schema(type=openapi.TYPE_ARRAY,
                                                items=openapi.Items(type=openapi.TYPE_OBJECT)),
                    'form-structure-data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)))
                }
            )
        ),
        400: 'Invalid form structure ID, filter list, or date format.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)