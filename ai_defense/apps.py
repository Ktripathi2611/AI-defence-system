from django.apps import AppConfig

class AiDefenseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_defense'

    def ready(self):
        from . import celery_monitor
        celery_monitor.start_monitor()
