from django.apps import AppConfig


class CustomadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customAdmin'

    def ready(self):
        import customAdmin.signals
