from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import redis
import json
from datetime import datetime
import psutil

@shared_task
def monitor_redis_stats():
    """Monitor Redis statistics and broadcast updates"""
    channel_layer = get_channel_layer()
    
    try:
        # Connect to Redis
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            socket_timeout=2,
            socket_connect_timeout=2
        )
        
        # Get Redis info
        info = redis_client.info()
        
        # Get peak clients from server info
        peak_clients = info.get('connected_clients', 0)  # Use current clients as peak if not available
        
        # Prepare stats
        stats = {
            'used_memory': info.get('used_memory', 0),
            'total_system_memory': psutil.virtual_memory().total,
            'connected_clients': info.get('connected_clients', 0),
            'connected_clients_peak': peak_clients,
            'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
            'uptime_in_seconds': info.get('uptime_in_seconds', 0),
            'last_save_time': info.get('rdb_last_save_time', 0),
        }
        
        # Broadcast to all Redis monitor WebSocket connections
        async_to_sync(channel_layer.group_send)(
            "redis_monitor",
            {
                "type": "redis_update",
                "data": {
                    'type': 'redis_stats',
                    'data': stats
                }
            }
        )
        
        return True
        
    except Exception as e:
        print(f"Error monitoring Redis: {str(e)}")
        # Broadcast error to WebSocket
        async_to_sync(channel_layer.group_send)(
            "redis_monitor",
            {
                "type": "redis_update",
                "data": {
                    'type': 'error',
                    'message': f'Redis monitoring error: {str(e)}'
                }
            }
        )
        return False

@shared_task
def scan_system_threats():
    """Scan system for potential threats"""
    channel_layer = get_channel_layer()
    
    try:
        threats = []
        
        # Check CPU usage spikes
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            threats.append({
                'type': 'resource',
                'severity': 'high',
                'message': f'High CPU usage detected: {cpu_percent}%'
            })
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            threats.append({
                'type': 'resource',
                'severity': 'high',
                'message': f'High memory usage detected: {memory.percent}%'
            })
        
        # Check disk usage
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                if usage.percent > 90:
                    threats.append({
                        'type': 'storage',
                        'severity': 'medium',
                        'message': f'Low disk space on {partition.mountpoint}: {usage.percent}%'
                    })
            except:
                continue
        
        # Get system stats for dashboard
        system_stats = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'threats': threats,
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast to dashboard
        async_to_sync(channel_layer.group_send)(
            "system_monitor",
            {
                "type": "system_update",
                "data": {
                    'type': 'system_stats',
                    'data': system_stats
                }
            }
        )
        
        return True
        
    except Exception as e:
        print(f"Error scanning threats: {str(e)}")
        return False

@shared_task
def update_ai_models():
    """Update AI models and broadcast status"""
    channel_layer = get_channel_layer()
    
    try:
        # Simulate AI model update process
        models = [
            {'name': 'Threat Detection', 'status': 'active', 'accuracy': '95%'},
            {'name': 'Anomaly Detection', 'status': 'active', 'accuracy': '92%'},
            {'name': 'Network Analysis', 'status': 'active', 'accuracy': '89%'},
            {'name': 'Pattern Recognition', 'status': 'training', 'progress': '76%'},
            {'name': 'Behavioral Analysis', 'status': 'active', 'accuracy': '91%'}
        ]
        
        update_status = {
            'models': models,
            'last_update': datetime.now().isoformat(),
            'next_update': 'in 1 hour'
        }
        
        # Broadcast update status
        async_to_sync(channel_layer.group_send)(
            "dashboard",
            {
                "type": "dashboard_update",
                "data": {
                    'type': 'ai_update',
                    'data': update_status
                }
            }
        )
        
        return True
        
    except Exception as e:
        print(f"Error updating AI models: {str(e)}")
        return False

@shared_task
def process_network_scan(scan_params):
    """Process network scan in background"""
    channel_layer = get_channel_layer()
    
    try:
        # Simulate network scanning process
        total_hosts = scan_params.get('ip_range', '').count('.')
        
        # Update progress periodically
        for progress in range(0, 101, 10):
            async_to_sync(channel_layer.group_send)(
                "network_scan",
                {
                    "type": "scan_update",
                    "data": {
                        'progress': progress,
                        'hosts_scanned': int(total_hosts * (progress/100)),
                        'status': 'scanning' if progress < 100 else 'completed'
                    }
                }
            )
            
            # Simulate scanning delay
            if progress < 100:
                # Removed asyncio.sleep(2) as it is not defined in the given code
                pass
        
        return True
        
    except Exception as e:
        print(f"Error during network scan: {str(e)}")
        return False
