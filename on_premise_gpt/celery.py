import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")

app = Celery("on_premise_gpt")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()