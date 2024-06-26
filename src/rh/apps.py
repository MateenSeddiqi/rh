from django.apps import AppConfig


class RhConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rh"
    verbose_name = "ReportHub"

    def ready(self):
        # ruff: noqa
        import rh.signals
