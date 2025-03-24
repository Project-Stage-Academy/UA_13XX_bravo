from django.apps import AppConfig


class Companies(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "companies"

    def ready(self):
        import companies.signals 