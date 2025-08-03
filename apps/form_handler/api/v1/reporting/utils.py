from collections import Counter
from rest_framework import status
from rest_framework.response import Response
from apps.form_handler.documents import FormStructure, FormRecord, FormRecordCell
from apps.form_handler.utils.time_handler import jalali_to_gregorian


def get_form_structure(form_structure_id):
    """
    Retrieves a FormStructure by ID, returns None if not found.
    """
    try:
        return FormStructure.objects.get(id=form_structure_id)
    except FormStructure.DoesNotExist:
        return None


def generate_filter_config(form_structure):
    """
    Generates filter configurations for a FormStructure based on column types.
    Returns a list of configuration dictionaries for int, str, and float columns.
    """
    filter_config = []
    for index, column in enumerate(form_structure.columns):
        if column.content_type == 'int':
            filter_config.extend([
                {
                    'type': 'int',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': index,
                    'condition_type': 'gte',
                    'condition_int': 0
                },
                {
                    'type': 'int',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': index,
                    'condition_type': 'lte',
                    'condition_int': 0
                }
            ])
        elif column.content_type == 'str':
            form_cells = FormRecordCell.objects.filter(form_structure_column=form_structure)
            content_counter = Counter(cell.content for cell in form_cells)
            content_list = list(content_counter.keys())
            filter_config.append({
                'type': 'str',
                'key_name': column.key_name,
                'name': column.title,
                'column_id': index,
                'content_list': content_list
            })
        elif column.content_type == 'float':
            filter_config.extend([
                {
                    'type': 'float',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': index,
                    'condition_type': 'gte',
                    'condition_int': 0
                },
                {
                    'type': 'float',
                    'key_name': column.key_name,
                    'name': column.title,
                    'column_id': index,
                    'condition_type': 'lte',
                    'condition_int': 0
                }
            ])
    return filter_config

def apply_form_filters(form_list, filter_list, post_data):
    """
    Applies filters to a queryset of forms based on date range and column conditions.
    Returns filtered forms or a Response object if an error occurs.
    """
    if date_from := post_data.get('data-from'):
        try:
            form_list = form_list.filter(create_date__gte=jalali_to_gregorian(date_from))
        except ValueError:
            return Response(
                {'message': 'Invalid start date format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    if date_to := post_data.get('data-to'):
        try:
            form_list = form_list.filter(create_date__lte=jalali_to_gregorian(date_to))
        except ValueError:
            return Response(
                {'message': 'Invalid end date format.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    filtered_forms = list(form_list)
    for flt in filter_list:
        if flt['type'] in ('int', 'float') and float(flt.get('condition_int', 0)) > 0:
            filtered_forms = _filter_numeric_values(filtered_forms, flt)
        elif flt['type'] == 'str' and flt.get('condition_str_list', []):
            filtered_forms = _filter_string_values(filtered_forms, flt)
    return filtered_forms

def _filter_numeric_values(form_list, flt):
    """
    Filters forms based on numeric (int/float) column values and conditions.
    Returns a list of forms that meet the condition.
    """
    condition_value = float(flt['condition_int'])
    content_type = 'float' if flt['type'] == 'float' else 'int'
    new_list = []
    for form in form_list:
        form_records = FormRecord.objects.filter(form=form)
        total = 0.0
        for record in form_records:
            form_cell_list = FormRecordCell.objects.filter(
                form_record=record,
                form_structure_column__columns__key_name=flt['key_name'],
                form_structure_column__columns__content_type=content_type
            )
            for cell in form_cell_list:
                try:
                    total += float(cell.content) if content_type == 'float' else int(cell.content)
                except (ValueError, TypeError):
                    continue
        if _apply_numeric_condition(total, condition_value, flt['condition_type']):
            new_list.append(form)
    return new_list

def _filter_string_values(form_list, flt):
    """
    Filters forms based on string column values matching the condition list.
    Returns a list of forms that meet the condition.
    """
    new_list = []
    for form in form_list:
        form_records = FormRecord.objects.filter(form=form)
        for record in form_records:
            form_cell_list = FormRecordCell.objects.filter(
                form_record=record,
                form_structure_column__columns__key_name=flt['key_name'],
                form_structure_column__columns__content_type='str'
            )
            for cell in form_cell_list:
                if cell.content in flt['condition_str_list']:
                    new_list.append(form)
                    break
            if form in new_list:
                break
    return new_list

def _apply_numeric_condition(total, condition_value, condition_type):
    """
    Applies numeric filter conditions (gt, gte, lt, lte) to a total value.
    Returns True if the condition is met, False otherwise.
    """
    if condition_type == 'gt':
        return total > condition_value
    elif condition_type == 'gte':
        return total >= condition_value
    elif condition_type == 'lt':
        return total < condition_value
    elif condition_type == 'lte':
        return total <= condition_value
    return False