from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from redis import Redis
from celery.app.control import Control
from django_celery_results.models import TaskResult
from datetime import timedelta
from django.utils import timezone
import redis

def home(request):
    return render(request, 'base.html')

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
    
    return render(request, 'dashboard.html', context)

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
    
    return render(request, 'threats.html', context)

def analytics(request):
    return render(request, 'analytics.html')

def settings_view(request):
    return render(request, 'settings.html')

def profile(request):
    return render(request, 'profile.html')

def system_logs(request):
    return render(request, 'logs.html')

def reports(request):
    return render(request, 'reports.html')

def ai_models(request):
    return render(request, 'ai_models.html')

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
    
    return render(request, 'network_scan.html', context)

def check_redis_status(request):
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        return JsonResponse({
            'status': 'online',
            'message': 'Redis server is running'
        })
    except redis.ConnectionError as e:
        return JsonResponse({
            'status': 'offline',
            'message': str(e)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

def check_celery_status(request):
    try:
        # Check for recent task activity
        recent_tasks = TaskResult.objects.filter(
            date_done__gte=timezone.now() - timedelta(minutes=5)
        ).exists()
        
        if recent_tasks:
            return JsonResponse({
                'status': 'online',
                'message': 'Celery worker is active'
            })
        else:
            return JsonResponse({
                'status': 'offline',
                'message': 'No recent Celery activity'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })
