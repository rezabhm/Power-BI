import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from apps.form_handler.models import UploadFile, FormStructure
from apps.form_handler.serializers import UploadFileSerializer, FormSerializer, FormRecordSerializer, FormRecordCellSerializer
from apps.form_handler.utils.detectFormStructure import detect_form_structure

def process_uploaded_file(excel_file, user):
    """
    Processes an uploaded Excel file to create forms, records, and cells based on detected form structures.
    Returns a Response object on error or None on success.
    """
    # Read Excel file
    try:
        file_data = pd.read_excel(excel_file)
    except Exception as e:
        return Response(
            {'message': f'Error reading file: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Detect form structures
    form_structure_ids = detect_form_structure(file_data)
    try:
        form_structure_list = [FormStructure.objects.get(id=form_id) for form_id in form_structure_ids]
    except ObjectDoesNotExist:
        return Response(
            {'message': 'One or more form structures not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not form_structure_list:
        return Response(
            {'message': 'Uploaded file does not match any form structures.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    file_name = excel_file.name
    file_header = file_data.columns.tolist()
    file_rows = file_data.values.tolist()

    # Check for duplicate file
    if UploadFile.objects.filter(file_name__exact=file_name).exists():
        return Response(
            {'message': 'This file has already been uploaded.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    used_objects = []
    try:
        for form_structure in form_structure_list:
            # Create Form
            form_data = {
                'form_structure': form_structure.id,
                'form_name': file_name,
                'user': user.id,
            }
            form_serializer = FormSerializer(data=form_data)
            if not form_serializer.is_valid():
                return _rollback_and_respond(used_objects, 'Error creating form', form_serializer.errors)

            form = form_serializer.save()
            used_objects.append(form)

            # Process each record
            for record in file_rows:
                # Create FormRecord
                form_record_data = {
                    'form': form.id,
                    'user': user.id,
                }
                form_record_serializer = FormRecordSerializer(data=form_record_data)
                if not form_record_serializer.is_valid():
                    return _rollback_and_respond(used_objects, 'Error creating form record', form_record_serializer.errors)

                form_record = form_record_serializer.save()
                used_objects.append(form_record)

                # Process each cell in the record
                for item_id, item in enumerate(record):
                    form_structure_column = _find_matching_column(form_structure, file_header[item_id])
                    if not form_structure_column:
                        return _rollback_and_respond(
                            used_objects,
                            'Invalid file format. Please correct the file according to the selected form structure.'
                        )

                    # Create FormRecordCell
                    record_cell_data = {
                        'form_record': form_record.id,
                        'form_structure_column': form_structure.id,
                        'user': user.id,
                        'content': str(item),
                    }
                    record_cell_serializer = FormRecordCellSerializer(data=record_cell_data)
                    if not record_cell_serializer.is_valid():
                        return _rollback_and_respond(used_objects, 'Error creating record cell', record_cell_serializer.errors)

                    record_cell = record_cell_serializer.save()
                    used_objects.append(record_cell)

            # Save the uploaded file
            uploaded_file_data = {
                'file_name': file_name,
                'user': user.id,
                'form_structure': form_structure.id,
            }
            uploaded_file_serializer = UploadFileSerializer(data=uploaded_file_data)
            if not uploaded_file_serializer.is_valid():
                return _rollback_and_respond(used_objects, 'Error saving uploaded file', uploaded_file_serializer.errors)

            uploaded_file = uploaded_file_serializer.save()
            used_objects.append(uploaded_file)

    except Exception as e:
        return _rollback_and_respond(used_objects, f'Unexpected error: {str(e)}')

    return None

def _find_matching_column(form_structure, excel_column_name):
    """
    Finds a matching FormStructureColumn by excel_column_name.
    Returns the matching column or None if not found.
    """
    for column in form_structure.columns:
        if column.excel_column_name == excel_column_name:
            return column
    return None

def _rollback_and_respond(used_objects, message, errors=None):
    """
    Deletes created objects during a failed operation and returns an error Response.
    """
    for obj in used_objects:
        obj.delete()
    response_data = {'message': message}
    if errors:
        response_data['errors'] = errors
    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)