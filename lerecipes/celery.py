import os
from celery import Celery
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lerecipes.settings')

app = Celery('lerecipes')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()