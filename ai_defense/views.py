import json
import subprocess
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import psutil

SERVICE_COMMANDS = {
    'redis': {
        'start': ['Redis/redis-server.exe', 'Redis/redis.conf'],
        'stop': lambda: [p.terminate() for p in psutil.process_iter() if 'redis-server' in p.name().lower()]
    },
    'celery-worker': {
        'start': ['celery', '-A', 'ai_defense', 'worker', '--pool=solo', '-l', 'info'],
        'stop': lambda: [p.terminate() for p in psutil.process_iter() if 'celery' in p.name().lower() and 'worker' in ' '.join(p.cmdline()).lower()]
    },
    'celery-beat': {
        'start': ['celery', '-A', 'ai_defense', 'beat', '-l', 'info'],
        'stop': lambda: [p.terminate() for p in psutil.process_iter() if 'celery' in p.name().lower() and 'beat' in ' '.join(p.cmdline()).lower()]
    },
    'flower': {
        'start': ['celery', '-A', 'ai_defense', 'flower'],
        'stop': lambda: [p.terminate() for p in psutil.process_iter() if 'flower' in ' '.join(p.cmdline()).lower()]
    }
}

def get_service_status(service_name):
    if service_name == 'redis':
        return any('redis-server' in p.name().lower() for p in psutil.process_iter())
    elif service_name == 'celery-worker':
        return any('celery' in p.name().lower() and 'worker' in ' '.join(p.cmdline()).lower() for p in psutil.process_iter())
    elif service_name == 'celery-beat':
        return any('celery' in p.name().lower() and 'beat' in ' '.join(p.cmdline()).lower() for p in psutil.process_iter())
    elif service_name == 'flower':
        return any('flower' in ' '.join(p.cmdline()).lower() for p in psutil.process_iter())
    return False

@csrf_exempt
@require_http_methods(["POST"])
def control_service(request, service, action):
    if service not in SERVICE_COMMANDS or action not in ['start', 'stop']:
        return JsonResponse({'status': 'error', 'message': 'Invalid service or action'})

    try:
        if action == 'start' and not get_service_status(service):
            command = SERVICE_COMMANDS[service]['start']
            subprocess.Popen(command, 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           cwd=os.path.dirname(os.path.dirname(__file__)))
            
        elif action == 'stop':
            SERVICE_COMMANDS[service]['stop']()

        return JsonResponse({
            'status': 'success',
            'message': f'{service} {action} command executed successfully'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })

@require_http_methods(["GET"])
def get_services_status(request):
    statuses = {
        service: get_service_status(service)
        for service in SERVICE_COMMANDS.keys()
    }
    return JsonResponse(statuses)
