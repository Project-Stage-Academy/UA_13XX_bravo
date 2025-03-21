from django.apps import AppConfig


class InvestmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "investments"


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notifications"

    def ready(self):
        import notifications.signals
