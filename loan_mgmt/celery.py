import os
from celery import Celery

# Ensure the Django settings module is set for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_mgmt.settings')

app = Celery('loan_mgmt')

# Read broker & backend settings from Django settings, CELERY_* keys
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover @shared_task modules in installed apps
app.autodiscover_tasks()