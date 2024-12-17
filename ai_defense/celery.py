import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_defense.settings')

# Create the Celery app
app = Celery('ai_defense')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered Django app configs
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'monitor-redis-stats': {
        'task': 'core.tasks.monitor_redis_stats',
        'schedule': 10.0,  # every 10 seconds
    },
    'scan-system-threats': {
        'task': 'core.tasks.scan_system_threats',
        'schedule': 30.0,  # every 30 seconds
    },
    'update-ai-models': {
        'task': 'core.tasks.update_ai_models',
        'schedule': 300.0,  # every 5 minutes
    },
}

# Optional configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
