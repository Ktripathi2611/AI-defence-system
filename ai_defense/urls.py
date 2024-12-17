from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('threats/', TemplateView.as_view(template_name='threats.html'), name='threats'),
    path('settings/', TemplateView.as_view(template_name='settings.html'), name='settings'),
    path('tools/ai-models/', TemplateView.as_view(template_name='ai_models.html'), name='ai_models'),
    path('tools/network-scan/', TemplateView.as_view(template_name='network_scan.html'), name='network_scan'),
    path('logs/', TemplateView.as_view(template_name='logs.html'), name='logs'),
    path('reports/', TemplateView.as_view(template_name='reports.html'), name='reports'),
    
    # API endpoints
    path('api/services/<str:service>/<str:action>/', views.control_service, name='control_service'),
    path('api/services/status/', views.get_services_status, name='services_status'),
]
