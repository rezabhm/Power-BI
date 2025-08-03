from collections import Counter
from typing import List
from apps.form_handler.documents import FormStructure
from apps.form_handler.serializers import FormStructureSerializer
import logging

# Configure logging
logger = logging.getLogger(__name__)

def detect_form_structure(file_pd) -> List[int]:
    """
    Detects matching FormStructure IDs based on column names in the provided pandas DataFrame.

    Args:
        file_pd (pandas.DataFrame): The input DataFrame containing column names to match against FormStructure columns.

    Returns:
        List[int]: A list of FormStructure IDs that match the column structure of the input file.

    The function compares the column names of the input DataFrame with the excel_column_name fields
    of all FormStructure objects. A match is found when the column names exactly match the
    excel_column_name values of a FormStructure's columns.
    """
    # Extract column names from the DataFrame
    file_columns = file_pd.columns.tolist()

    # Retrieve all FormStructure objects and serialize them
    form_structures = FormStructure.objects.all()
    serializer = FormStructureSerializer(form_structures, many=True)
    form_structure_data = serializer.data

    # List to store IDs of matching FormStructures
    detected_forms = []

    for form in form_structure_data:
        # Extract excel_column_name values from the form's columns
        form_columns = [column['excel_column_name'] for column in form.get('columns', [])]

        # Check if the number of columns matches
        if len(form_columns) != len(file_columns):
            continue

        # Use Counter to compare column names
        column_counter = Counter(form_columns + file_columns)

        # Check if all columns appear exactly twice (once in form, once in file)
        is_match = all(count == 2 for count in column_counter.values())

        if is_match:
            detected_forms.append(form['id'])

    # Log the detected FormStructure IDs
    logger.debug("Detected form structure IDs: %s", detected_forms)

    return detected_forms