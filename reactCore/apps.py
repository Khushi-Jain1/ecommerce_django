from django.apps import AppConfig


class ReactcoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reactCore'

    def ready(self) -> None:
        import customAdmin.signals
