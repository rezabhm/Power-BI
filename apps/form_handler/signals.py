from mongoengine import signals

from apps.form_handler.documents import Folder, FormStructure, Form, FormRecord, UploadFile, FormRecordCell


def setup_signals():

    # Signal for Folder: Cascade delete FormStructures
    def folder_pre_delete(cls, sender, document, **kwargs):
        FormStructure.objects(folder=document).delete()

    signals.pre_delete.connect(folder_pre_delete, sender=Folder)

    # Signal for FormStructure: Cascade delete Forms and UploadFiles
    def form_structure_pre_delete(cls, sender, document, **kwargs):
        Form.objects(form_structure=document).delete()
        UploadFile.objects(form_structure=document).delete()

    signals.pre_delete.connect(form_structure_pre_delete, sender=FormStructure)

    # Signal for Form: Cascade delete FormRecords
    def form_pre_delete(cls, sender, document, **kwargs):
        FormRecord.objects(form=document).delete()

    signals.pre_delete.connect(form_pre_delete, sender=Form)

    # Signal for FormRecord: Cascade delete FormRecordCells
    def form_record_pre_delete(cls, sender, document, **kwargs):
        FormRecordCell.objects(form_record=document).delete()

    signals.pre_delete.connect(form_record_pre_delete, sender=FormRecord)

