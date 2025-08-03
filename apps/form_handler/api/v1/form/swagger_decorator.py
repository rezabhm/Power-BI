from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from apps.form_handler.serializers import (
    FolderSerializer, FolderTypeSerializer, FolderTypeListSerializer,
    FormStructureSerializer, FormStructureListSerializer, FormStructureColumnSerializer,
    FormStructureSpecificationsSerializer, FormSerializer, FormListSerializer,
    FormRecordSerializer, FormRecordListSerializer, FormRecordCellSerializer,
    FormRecordCellListSerializer, UploadFileSerializer
)

# FolderViewSet Swagger Decorators
folder_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Folder',
    operation_description=(
        'Allows authenticated users to create a new folder. '
        'Requires valid folder data in the request body. '
        'Returns the created folder details.'
    ),
    tags=['form_handler.folder'],
    request_body=FolderSerializer,
    responses={
        201: FolderSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

folder_retrieve_swagger = swagger_auto_schema(
    operation_summary='Retrieve Folder Details',
    operation_description=(
        'Allows authenticated users to retrieve details of a folder by ID. '
        'Returns details including ID, name, and creation date.'
    ),
    tags=['form_handler.folder'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the folder to retrieve.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FolderSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Folder with the specified ID does not exist.'
    }
)

folder_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Folder',
    operation_description=(
        'Allows authenticated users to fully update a folder by ID. '
        'Requires all folder fields in the request body. '
        'Returns the updated folder details.'
    ),
    tags=['form_handler.folder'],
    request_body=FolderSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the folder to update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FolderSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Folder with the specified ID does not exist.'
    }
)

folder_partial_update_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Folder',
    operation_description=(
        'Allows authenticated users to partially update a folder by ID. '
        'Only provided fields are updated. '
        'Returns the updated folder details.'
    ),
    tags=['form_handler.folder'],
    request_body=FolderSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the folder to partially update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FolderSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Folder with the specified ID does not exist.'
    }
)

folder_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Folder',
    operation_description=(
        'Allows authenticated users to delete a folder by ID. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.folder'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the folder to delete.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Folder successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Folder with the specified ID does not exist.'
    }
)

folder_list_swagger = swagger_auto_schema(
    operation_summary='List All Folders',
    operation_description=(
        'Allows authenticated users to retrieve a list of all folders. '
        'Returns details for each folder, ordered by creation date (newest first).'
    ),
    tags=['form_handler.folder'],
    responses={
        200: FolderSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

# FolderTypeViewSet Swagger Decorators
folder_type_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Folder Type',
    operation_description=(
        'Allows authenticated users to create a new folder type. '
        'Requires valid folder type data in the request body. '
        'Returns the created folder type details.'
    ),
    tags=['form_handler.folder_type'],
    request_body=FolderTypeSerializer,
    responses={
        201: FolderTypeSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

folder_type_list_swagger = swagger_auto_schema(
    operation_summary='List All Folder Types',
    operation_description=(
        'Allows authenticated users to retrieve a list of all folder types. '
        'Returns details for each folder type.'
    ),
    tags=['form_handler.folder_type'],
    responses={
        200: FolderTypeListSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

folder_type_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Folder Type',
    operation_description=(
        'Allows authenticated users to fully update a folder type by ID. '
        'Requires all folder type fields in the request body. '
        'Returns the updated folder type details.'
    ),
    tags=['form_handler.folder_type'],
    request_body=FolderTypeSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the folder type to update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FolderTypeSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Folder type with the specified ID does not exist.'
    }
)

folder_type_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Folder Type',
    operation_description=(
        'Allows authenticated users to delete a folder type by ID. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.folder_type'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the folder type to delete.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Folder type successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Folder type with the specified ID does not exist.'
    }
)

# FormStructureViewSet Swagger Decorators
form_structure_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Form Structure',
    operation_description=(
        'Allows authenticated users to create a new form structure, optionally linked to a folder. '
        'Requires valid form structure data in the request body. '
        'Returns the created form structure details.'
    ),
    tags=['form_handler.form_structure'],
    request_body=FormStructureSerializer,
    responses={
        201: FormStructureSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

form_structure_retrieve_swagger = swagger_auto_schema(
    operation_summary='Retrieve Form Structure Details',
    operation_description=(
        'Allows authenticated users to retrieve details of a form structure by ID. '
        'Returns details including ID, folder, and creation date.'
    ),
    tags=['form_handler.form_structure'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form structure to retrieve.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Form Structure',
    operation_description=(
        'Allows authenticated users to fully update a form structure by ID. '
        'Requires all form structure fields in the request body. '
        'Returns the updated form structure details.'
    ),
    tags=['form_handler.form_structure'],
    request_body=FormStructureSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form structure to update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_partial_update_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Form Structure',
    operation_description=(
        'Allows authenticated users to partially update a form structure by ID. '
        'Only provided fields are updated. '
        'Returns the updated form structure details.'
    ),
    tags=['form_handler.form_structure'],
    request_body=FormStructureSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form structure to partially update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Form Structure',
    operation_description=(
        'Allows authenticated users to delete a form structure by ID. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.form_structure'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form structure to delete.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Form structure successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_list_swagger = swagger_auto_schema(
    operation_summary='List All Form Structures',
    operation_description=(
        'Allows authenticated users to retrieve a list of form structures, optionally filtered by folder ID. '
        'Returns details for each form structure, ordered by creation date (newest first).'
    ),
    tags=['form_handler.form_structure'],
    manual_parameters=[
        openapi.Parameter('folder_pk', openapi.IN_PATH, description='Optional folder ID to filter form structures.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureListSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

# FormStructureColumnViewSet Swagger Decorators
form_structure_column_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Form Structure Column',
    operation_description=(
        'Allows authenticated users to create a new column for a specific form structure. '
        'Requires valid column data and form_structure_id in the URL. '
        'The column is appended to the form structure’s columns list.'
    ),
    tags=['form_handler.form_structure_column'],
    request_body=FormStructureColumnSerializer,
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        201: FormStructureColumnSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_column_list_swagger = swagger_auto_schema(
    operation_summary='List Form Structure Columns',
    operation_description=(
        'Allows authenticated users to retrieve a list of columns for a specific form structure. '
        'Requires form_structure_id in the URL.'
    ),
    tags=['form_handler.form_structure_column'],
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureColumnSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_column_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Form Structure Column',
    operation_description=(
        'Allows authenticated users to fully update a column by index in a form structure. '
        'Requires form_structure_id and column index (pk) in the URL. '
        'Returns the updated column details.'
    ),
    tags=['form_handler.form_structure_column'],
    request_body=FormStructureColumnSerializer,
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER),
        openapi.Parameter('pk', openapi.IN_PATH, description='Index of the column in the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureColumnSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure or column not found.'
    }
)

form_structure_column_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Form Structure Column',
    operation_description=(
        'Allows authenticated users to delete a column by index from a form structure. '
        'Requires form_structure_id and column index (pk) in the URL. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.form_structure_column'],
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER),
        openapi.Parameter('pk', openapi.IN_PATH, description='Index of the column in the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Column successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure or column not found.'
    }
)

# FormStructureSpecificationViewSet Swagger Decorators
form_structure_spec_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Form Structure Specification',
    operation_description=(
        'Allows authenticated users to create a new specification for a specific form structure. '
        'Requires valid specification data and form_structure_id in the URL. '
        'The specification is appended to the form structure’s specifications list.'
    ),
    tags=['form_handler.form_structure_specification'],
    request_body=FormStructureSpecificationsSerializer,
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        201: FormStructureSpecificationsSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_spec_list_swagger = swagger_auto_schema(
    operation_summary='List Form Structure Specifications',
    operation_description=(
        'Allows authenticated users to retrieve a list of specifications for a specific form structure. '
        'Requires form_structure_id in the URL.'
    ),
    tags=['form_handler.form_structure_specification'],
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureSpecificationsSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure with the specified ID does not exist.'
    }
)

form_structure_spec_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Form Structure Specification',
    operation_description=(
        'Allows authenticated users to fully update a specification by index in a form structure. '
        'Requires form_structure_id and specification index (pk) in the URL. '
        'Returns the updated specification details.'
    ),
    tags=['form_handler.form_structure_specification'],
    request_body=FormStructureSpecificationsSerializer,
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER),
        openapi.Parameter('pk', openapi.IN_PATH, description='Index of the specification in the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormStructureSpecificationsSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure or specification not found.'
    }
)

form_structure_spec_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Form Structure Specification',
    operation_description=(
        'Allows authenticated users to delete a specification by index from a form structure. '
        'Requires form_structure_id and specification index (pk) in the URL. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.form_structure_specification'],
    manual_parameters=[
        openapi.Parameter('form_structure_id', openapi.IN_PATH, description='Unique ID of the form structure.', type=openapi.TYPE_INTEGER),
        openapi.Parameter('pk', openapi.IN_PATH, description='Index of the specification in the form structure.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Specification successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form structure or specification not found.'
    }
)

# FormViewSet Swagger Decorators
form_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Form',
    operation_description=(
        'Allows authenticated users to create a new form. '
        'Requires valid form data in the request body. '
        'Returns the created form details.'
    ),
    tags=['form_handler.form'],
    request_body=FormSerializer,
    responses={
        201: FormSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

form_retrieve_swagger = swagger_auto_schema(
    operation_summary='Retrieve Form Details',
    operation_description=(
        'Allows authenticated users to retrieve details of a form by ID. '
        'Returns details including ID, name, and creation date.'
    ),
    tags=['form_handler.form'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form to retrieve.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form with the specified ID does not exist.'
    }
)

form_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Form',
    operation_description=(
        'Allows authenticated users to fully update a form by ID. '
        'Requires all form fields in the request body. '
        'Returns the updated form details.'
    ),
    tags=['form_handler.form'],
    request_body=FormSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form to update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form with the specified ID does not exist.'
    }
)

form_partial_update_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Form',
    operation_description=(
        'Allows authenticated users to partially update a form by ID. '
        'Only provided fields are updated. '
        'Returns the updated form details.'
    ),
    tags=['form_handler.form'],
    request_body=FormSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form to partially update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form with the specified ID does not exist.'
    }
)

form_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Form',
    operation_description=(
        'Allows authenticated users to delete a form by ID. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.form'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form to delete.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Form successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form with the specified ID does not exist.'
    }
)

form_list_swagger = swagger_auto_schema(
    operation_summary='List All Forms',
    operation_description=(
        'Allows authenticated users to retrieve a list of all forms. '
        'Returns details for each form, ordered by creation date (newest first).'
    ),
    tags=['form_handler.form'],
    responses={
        200: FormListSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

# FormRecordViewSet Swagger Decorators
form_record_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Form Record',
    operation_description=(
        'Allows authenticated users to create a new form record. '
        'Requires valid form record data in the request body. '
        'Returns the created form record details.'
    ),
    tags=['form_handler.form_record'],
    request_body=FormRecordSerializer,
    responses={
        201: FormRecordSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

form_record_retrieve_swagger = swagger_auto_schema(
    operation_summary='Retrieve Form Record Details',
    operation_description=(
        'Allows authenticated users to retrieve details of a form record by ID. '
        'Returns details including ID and creation date.'
    ),
    tags=['form_handler.form_record'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record to retrieve.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormRecordSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record with the specified ID does not exist.'
    }
)

form_record_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Form Record',
    operation_description=(
        'Allows authenticated users to fully update a form record by ID. '
        'Requires all form record fields in the request body. '
        'Returns the updated form record details.'
    ),
    tags=['form_handler.form_record'],
    request_body=FormRecordSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record to update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormRecordSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record with the specified ID does not exist.'
    }
)

form_record_partial_update_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Form Record',
    operation_description=(
        'Allows authenticated users to partially update a form record by ID. '
        'Only provided fields are updated. '
        'Returns the updated form record details.'
    ),
    tags=['form_handler.form_record'],
    request_body=FormRecordSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record to partially update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormRecordSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record with the specified ID does not exist.'
    }
)

form_record_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Form Record',
    operation_description=(
        'Allows authenticated users to delete a form record by ID. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.form_record'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record to delete.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Form record successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record with the specified ID does not exist.'
    }
)

form_record_list_swagger = swagger_auto_schema(
    operation_summary='List All Form Records',
    operation_description=(
        'Allows authenticated users to retrieve a list of all form records. '
        'Returns details for each form record, ordered by creation date (newest first).'
    ),
    tags=['form_handler.form_record'],
    responses={
        200: FormRecordListSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

# FormRecordCellViewSet Swagger Decorators
form_record_cell_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Form Record Cell',
    operation_description=(
        'Allows authenticated users to create a new form record cell. '
        'Requires valid form record cell data in the request body. '
        'Returns the created form record cell details.'
    ),
    tags=['form_handler.form_record_cell'],
    request_body=FormRecordCellSerializer,
    responses={
        201: FormRecordCellSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

form_record_cell_retrieve_swagger = swagger_auto_schema(
    operation_summary='Retrieve Form Record Cell Details',
    operation_description=(
        'Allows authenticated users to retrieve details of a form record cell by ID. '
        'Returns details including ID and creation date.'
    ),
    tags=['form_handler.form_record_cell'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record cell to retrieve.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormRecordCellSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record cell with the specified ID does not exist.'
    }
)

form_record_cell_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update a Form Record Cell',
    operation_description=(
        'Allows authenticated users to fully update a form record cell by ID. '
        'Requires all form record cell fields in the request body. '
        'Returns the updated form record cell details.'
    ),
    tags=['form_handler.form_record_cell'],
    request_body=FormRecordCellSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record cell to update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormRecordCellSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record cell with the specified ID does not exist.'
    }
)

form_record_cell_partial_update_swagger = swagger_auto_schema(
    operation_summary='Partially Update a Form Record Cell',
    operation_description=(
        'Allows authenticated users to partially update a form record cell by ID. '
        'Only provided fields are updated. '
        'Returns the updated form record cell details.'
    ),
    tags=['form_handler.form_record_cell'],
    request_body=FormRecordCellSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record cell to partially update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: FormRecordCellSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record cell with the specified ID does not exist.'
    }
)

form_record_cell_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete a Form Record Cell',
    operation_description=(
        'Allows authenticated users to delete a form record cell by ID. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.form_record_cell'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the form record cell to delete.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Form record cell successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Form record cell with the specified ID does not exist.'
    }
)

form_record_cell_list_swagger = swagger_auto_schema(
    operation_summary='List All Form Record Cells',
    operation_description=(
        'Allows authenticated users to retrieve a list of all form record cells. '
        'Returns details for each form record cell, ordered by creation date (newest first).'
    ),
    tags=['form_handler.form_record_cell'],
    responses={
        200: FormRecordCellListSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)

# UploadFileViewSet Swagger Decorators
upload_file_create_swagger = swagger_auto_schema(
    operation_summary='Create a New Uploaded File',
    operation_description=(
        'Allows authenticated users to create a new uploaded file. '
        'Requires valid file data in the request body. '
        'Returns the created file details.'
    ),
    tags=['form_handler.upload_file'],
    request_body=UploadFileSerializer,
    responses={
        201: UploadFileSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.'
    }
)

upload_file_retrieve_swagger = swagger_auto_schema(
    operation_summary='Retrieve Uploaded File Details',
    operation_description=(
        'Allows authenticated users to retrieve details of an uploaded file by ID. '
        'Returns details including ID, file name, and upload date.'
    ),
    tags=['form_handler.upload_file'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the uploaded file to retrieve.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: UploadFileSerializer,
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Uploaded file with the specified ID does not exist.'
    }
)

upload_file_update_swagger = swagger_auto_schema(
    operation_summary='Fully Update an Uploaded File',
    operation_description=(
        'Allows authenticated users to fully update an uploaded file by ID. '
        'Requires all file fields in the request body. '
        'Returns the updated file details.'
    ),
    tags=['form_handler.upload_file'],
    request_body=UploadFileSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the uploaded file to update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: UploadFileSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Uploaded file with the specified ID does not exist.'
    }
)

upload_file_partial_update_swagger = swagger_auto_schema(
    operation_summary='Partially Update an Uploaded File',
    operation_description=(
        'Allows authenticated users to partially update an uploaded file by ID. '
        'Only provided fields are updated. '
        'Returns the updated file details.'
    ),
    tags=['form_handler.upload_file'],
    request_body=UploadFileSerializer,
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the uploaded file to partially update.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: UploadFileSerializer,
        400: 'Invalid input data.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Uploaded file with the specified ID does not exist.'
    }
)

upload_file_destroy_swagger = swagger_auto_schema(
    operation_summary='Delete an Uploaded File',
    operation_description=(
        'Allows authenticated users to delete an uploaded file by ID. '
        'Returns a 204 No Content response upon successful deletion.'
    ),
    tags=['form_handler.upload_file'],
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_PATH, description='Unique ID of the uploaded file to delete.', type=openapi.TYPE_INTEGER)
    ],
    responses={
        204: 'Uploaded file successfully deleted.',
        401: 'Unauthorized: Valid JWT token required.',
        404: 'Uploaded file with the specified ID does not exist.'
    }
)

upload_file_list_swagger = swagger_auto_schema(
    operation_summary='List All Uploaded Files',
    operation_description=(
        'Allows authenticated users to retrieve a list of all uploaded files. '
        'Returns details for each file, ordered by upload date (newest first).'
    ),
    tags=['form_handler.upload_file'],
    responses={
        200: UploadFileSerializer(many=True),
        401: 'Unauthorized: Valid JWT token required.'
    }
)