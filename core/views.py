from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from datetime import datetime, timedelta
from django.utils import timezone
import redis
import psutil

def add_security_headers(response):
    response['X-Frame-Options'] = 'DENY'
    response['X-Content-Type-Options'] = 'nosniff'
    response['X-XSS-Protection'] = '1; mode=block'
    response['Content-Security-Policy'] = "default-src 'self'"
    response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@login_required
@csrf_protect
def home(request):
    return render(request, 'base.html')

@login_required
@csrf_protect
def dashboard(request):
    # Sample default activities - in a real app, this would come from your database
    default_activities = [
        {
            'time': '2024-01-17 00:30:15',
            'event': 'Suspicious activity detected',
            'type': 'Threat',
            'type_class': 'danger',
            'status': 'Investigating',
            'status_class': 'warning'
        },
        {
            'time': '2024-01-17 00:25:45',
            'event': 'Model update completed',
            'type': 'AI Model',
            'type_class': 'primary',
            'status': 'Completed',
            'status_class': 'success'
        },
        {
            'time': '2024-01-17 00:20:30',
            'event': 'Backup completed successfully',
            'type': 'System',
            'type_class': 'info',
            'status': 'Completed',
            'status_class': 'success'
        }
    ]

    # Sample statistics - in a real app, these would be calculated from your database
    stats = {
        'active_threats': 3,
        'system_health': 98,
        'active_models': 5,
        'alerts_today': 12
    }

    context = {
        'default_activities': default_activities,
        'stats': stats
    }
    
    response = render(request, 'dashboard.html', context)
    return add_security_headers(response)

@login_required
@csrf_protect
def threats(request):
    # Sample threat data - in a real app, this would come from your database
    threats_data = [
        {
            'id': 'THR-001',
            'type': 'Ransomware',
            'source': '192.168.1.100',
            'target': '/var/www/html',
            'severity': 'High',
            'status': 'Active',
            'detected': '2024-12-17 01:00',
            'progress': '75%'
        },
        {
            'id': 'THR-002',
            'type': 'Brute Force',
            'source': '45.67.89.123',
            'target': 'SSH Service',
            'severity': 'Medium',
            'status': 'Investigating',
            'detected': '2024-12-17 00:45',
            'progress': '45%'
        }
    ]

    # Statistics for the overview cards
    stats = {
        'active_threats': 3,
        'investigating_threats': 2,
        'resolved_threats': 5,
        'detection_rate': 98
    }

    context = {
        'threats': threats_data,
        'active_threats': stats['active_threats'],
        'investigating_threats': stats['investigating_threats'],
        'resolved_threats': stats['resolved_threats'],
        'detection_rate': stats['detection_rate']
    }
    
    response = render(request, 'threats.html', context)
    return add_security_headers(response)

@login_required
@csrf_protect
def analytics(request):
    response = render(request, 'analytics.html')
    return add_security_headers(response)

@login_required
@csrf_protect
def settings_view(request):
    response = render(request, 'settings.html')
    return add_security_headers(response)

@login_required
@csrf_protect
def profile(request):
    response = render(request, 'profile.html')
    return add_security_headers(response)

@login_required
@csrf_protect
def system_logs(request):
    response = render(request, 'logs.html')
    return add_security_headers(response)

@login_required
@csrf_protect
def reports(request):
    response = render(request, 'reports.html')
    return add_security_headers(response)

@login_required
@csrf_protect
def ai_models(request):
    response = render(request, 'ai_models.html')
    return add_security_headers(response)

@login_required
@csrf_protect
def network_scan(request):
    # Sample network scan results - in a real app, this would come from actual network scans
    scan_results = [
        {
            'ip': '192.168.1.100',
            'host': 'workstation-1',
            'status': 'Online',
            'open_ports': '80, 443, 3389',
            'services': 'HTTP, HTTPS, RDP',
            'os': 'Windows 10',
            'risk_level': 'Medium'
        },
        {
            'ip': '192.168.1.101',
            'host': 'server-1',
            'status': 'Online',
            'open_ports': '22, 80, 443',
            'services': 'SSH, HTTP, HTTPS',
            'os': 'Ubuntu 20.04',
            'risk_level': 'Low'
        }
    ]
    
    context = {
        'scan_results': scan_results
    }
    
    response = render(request, 'network_scan.html', context)
    return add_security_headers(response)

@login_required
def check_redis_status(request):
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_info = redis_client.info()
        status = 'running' if redis_info else 'stopped'
    except:
        status = 'stopped'
    
    response = JsonResponse({'status': status})
    return add_security_headers(response)

@login_required
def check_celery_status(request):
    try:
        # Check if Celery process is running
        celery_running = any('celery' in p.name().lower() for p in psutil.process_iter())
        status = 'running' if celery_running else 'stopped'
    except:
        status = 'stopped'
    
    response = JsonResponse({'status': status})
    return add_security_headers(response)
