from collections import Counter
from apps.form_handler.documents import FormStructure
from apps.form_handler.serializers import FormStructureSerializer

def detect_form_structure(file_pd):
    columns = file_pd.columns.tolist()

    form_structure_list = FormStructure.objects.all()
    form_structure_serializer = FormStructureSerializer(form_structure_list, many=True)
    form_structure_list = form_structure_serializer.data

    detected_form = []

    for form in form_structure_list:
        form_column_list = [clm['excel_column_name'] for clm in form.get('columns', [])]

        column_counter = Counter(form_column_list + columns)
        status = True

        if len(form_column_list) == len(columns):
            for key in column_counter:
                if column_counter[key] <= 1:
                    status = False
                    break
        else:
            status = False

        if status:
            detected_form.append(form['id'])

    print(f'\n\ndetected form: {detected_form}')
    return detected_form
