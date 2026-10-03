from django.apps import AppConfig


class StrategicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "strategic"

    def ready(self):
        from .license_check import check_license
        check_license()
