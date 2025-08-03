from django.apps import AppConfig
from django.conf import settings
from mongoengine import connect

from apps.form_handler.signals import setup_signals


class FormHandlerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.form_handler'
    label = 'form_handler'

    def ready(self):
        mongodb_settings = settings.MONGODB_SETTINGS
        connect(**mongodb_settings)

        # mongoDB signals
        setup_signals()
