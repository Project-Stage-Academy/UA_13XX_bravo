import os
from celery import Celery

# Set default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UA_13XX_bravo.settings')

# Create Celery app instance
celery_app = Celery('UA_13XX_bravo')

# Load configuration from Django settings (CELERY_ namespace)
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all Django apps
celery_app.autodiscover_tasks()

# Optional debug task
@celery_app.task(bind=True)
def debug_task(self):
    print(f"[CELERY DEBUG] Request: {self.request!r}")
