from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  
    path('api/status/redis', views.check_redis_status, name='redis_status'),
    path('api/status/celery', views.check_celery_status, name='celery_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('threats/', views.threats, name='threats'),
    path('analytics/', views.analytics, name='analytics'),
    path('settings/', views.settings_view, name='settings'),
    path('profile/', views.profile, name='profile'),
    path('logs/', views.system_logs, name='logs'),
    path('reports/', views.reports, name='reports'),
    path('ai-models/', views.ai_models, name='ai_models'),
    path('network-scan/', views.network_scan, name='network_scan'),
]
