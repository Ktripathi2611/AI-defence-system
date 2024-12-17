import json
import psutil
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from datetime import datetime
import redis
import os
import asyncio

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("dashboard", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'request_update':
            # Send current stats
            await self.send_dashboard_update()

    async def dashboard_update(self, event):
        """Handle dashboard updates"""
        await self.send(text_data=json.dumps(event['data']))

    async def send_dashboard_update(self):
        """Send current dashboard stats"""
        stats = {
            'active_threats': 3,
            'system_health': 98,
            'active_models': 5,
            'alerts_today': 12,
            'timestamp': datetime.now().isoformat()
        }
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': stats
        }))

class ThreatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("threats", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("threats", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'request_update':
            await self.send_threat_update()

    async def threat_update(self, event):
        """Handle threat updates"""
        await self.send(text_data=json.dumps(event['data']))

    async def send_threat_update(self):
        """Send current threat data"""
        threats = [
            {
                'id': 'THR-001',
                'type': 'Ransomware',
                'source': '192.168.1.100',
                'target': '/var/www/html',
                'severity': 'High',
                'status': 'Active',
                'detected': datetime.now().isoformat(),
                'progress': '75%'
            }
        ]
        await self.send(text_data=json.dumps({
            'type': 'threat_update',
            'data': {'threats': threats}
        }))

class NetworkScanConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("network_scan", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("network_scan", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'start_scan':
            await self.start_network_scan(text_data_json.get('data', {}))
        elif message_type == 'request_update':
            await self.send_scan_update()

    async def scan_update(self, event):
        """Handle scan updates"""
        await self.send(text_data=json.dumps(event['data']))

    async def start_network_scan(self, scan_params):
        """Start a network scan"""
        # In a real implementation, this would initiate an actual network scan
        await self.send(text_data=json.dumps({
            'type': 'scan_started',
            'data': {
                'scan_id': 'SCAN-001',
                'status': 'running',
                'start_time': datetime.now().isoformat()
            }
        }))

    async def send_scan_update(self):
        """Send current scan results"""
        results = [
            {
                'ip': '192.168.1.100',
                'host': 'workstation-1',
                'status': 'Online',
                'open_ports': '80, 443, 3389',
                'services': 'HTTP, HTTPS, RDP',
                'os': 'Windows 10',
                'risk_level': 'Medium',
                'scan_time': datetime.now().isoformat()
            }
        ]
        await self.send(text_data=json.dumps({
            'type': 'scan_update',
            'data': {'scan_results': results}
        }))

class RedisMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("redis_monitor", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("redis_monitor", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'request_update':
            await self.send_redis_stats()

    async def redis_update(self, event):
        """Handle Redis stats updates"""
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_redis_info(self):
        try:
            r = redis.Redis(host='localhost', port=6379, db=0)
            info = r.info()
            return {
                'connected': True,
                'used_memory': info['used_memory'],
                'total_system_memory': info['total_system_memory'],
                'connected_clients': info['connected_clients'],
                'connected_clients_peak': info['connected_clients_peak'],
                'instantaneous_ops_per_sec': info['instantaneous_ops_per_sec'],
                'uptime_in_seconds': info['uptime_in_seconds']
            }
        except (redis.ConnectionError, ConnectionRefusedError):
            return {
                'connected': False,
                'used_memory': 0,
                'total_system_memory': 0,
                'connected_clients': 0,
                'connected_clients_peak': 0,
                'instantaneous_ops_per_sec': 0,
                'uptime_in_seconds': 0
            }

    async def send_redis_stats(self):
        """Send Redis stats"""
        stats = await self.get_redis_info()
        await self.send(text_data=json.dumps({
            'type': 'redis_stats',
            'data': stats
        }))

class SystemMonitorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("system_monitor", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("system_monitor", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        
        if message_type == 'request_update':
            await self.send_system_stats()

    async def system_update(self, event):
        """Handle system stats updates"""
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_system_stats(self):
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'memory_total': memory.total,
            'memory_used': memory.used,
            'disk_total': disk.total,
            'disk_used': disk.used
        }

    async def send_system_stats(self):
        """Send system stats"""
        stats = await self.get_system_stats()
        await self.send(text_data=json.dumps({
            'type': 'system_stats',
            'data': stats
        }))

class ServiceControlConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("service_control", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("service_control", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')
        service = text_data_json.get('service', '')
        action = text_data_json.get('action', '')
        
        if message_type == 'service_control':
            await self.handle_service_control(service, action)

    @sync_to_async
    def handle_service_control(self, service, action):
        """Handle service control actions"""
        result = {'success': False, 'message': ''}
        
        try:
            if service == 'redis':
                if action == 'start':
                    os.system('redis-server')
                    result = {'success': True, 'message': 'Redis server started'}
                elif action == 'stop':
                    os.system('redis-cli shutdown')
                    result = {'success': True, 'message': 'Redis server stopped'}
            
            elif service == 'celery-worker':
                if action == 'start':
                    os.system('celery -A ai_defence_system worker --loglevel=info')
                    result = {'success': True, 'message': 'Celery worker started'}
                elif action == 'stop':
                    os.system('celery -A ai_defence_system control shutdown')
                    result = {'success': True, 'message': 'Celery worker stopped'}
            
            elif service == 'celery-beat':
                if action == 'start':
                    os.system('celery -A ai_defence_system beat --loglevel=info')
                    result = {'success': True, 'message': 'Celery beat started'}
                elif action == 'stop':
                    os.system('pkill -f "celery beat"')
                    result = {'success': True, 'message': 'Celery beat stopped'}
            
            elif service == 'flower':
                if action == 'start':
                    os.system('celery -A ai_defence_system flower')
                    result = {'success': True, 'message': 'Flower monitor started'}
                elif action == 'stop':
                    os.system('pkill -f "flower"')
                    result = {'success': True, 'message': 'Flower monitor stopped'}
            
        except Exception as e:
            result = {'success': False, 'message': str(e)}
        
        await self.send(text_data=json.dumps({
            'type': 'service_control_result',
            'data': result
        }))

class RedisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.redis_client = None
        self.update_task = None
        
    async def disconnect(self, close_code):
        await self.cleanup()
            
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data['type'] == 'control':
                action = data['action']
                if action == 'start':
                    await self.start_redis()
                elif action == 'stop':
                    await self.stop_redis()
            elif data['type'] == 'request_update':
                await self.send_redis_stats()
        except Exception as e:
            await self.send(json.dumps({
                'type': 'redis_status',
                'status': 'error',
                'message': f'Error processing request: {str(e)}'
            }))
            
    async def cleanup(self):
        """Clean up Redis connection and tasks"""
        if self.update_task and not self.update_task.done():
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
        self.update_task = None
        self.redis_client = None
            
    async def start_redis(self):
        try:
            if self.redis_client:
                raise Exception("Redis client already connected")
            
            # Connect to Redis
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_client.ping()  # Test connection
            
            # Start periodic updates
            await self.cleanup()  # Cleanup any existing tasks
            self.update_task = asyncio.create_task(self.periodic_update())
            
            await self.send(json.dumps({
                'type': 'redis_status',
                'status': 'connected',
                'message': 'Connected to Redis server'
            }))
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error connecting to Redis: {error_msg}")
            await self.cleanup()
            await self.send(json.dumps({
                'type': 'redis_status',
                'status': 'error',
                'message': f'Failed to connect to Redis: {error_msg}'
            }))
            
    async def stop_redis(self):
        try:
            if not self.redis_client:
                raise Exception("Redis client not connected")
            
            await self.cleanup()
            await self.send(json.dumps({
                'type': 'redis_status',
                'status': 'disconnected',
                'message': 'Disconnected from Redis server'
            }))
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error disconnecting from Redis: {error_msg}")
            await self.cleanup()
            await self.send(json.dumps({
                'type': 'redis_status',
                'status': 'error',
                'message': f'Error disconnecting from Redis: {error_msg}'
            }))
            
    async def periodic_update(self):
        while True:
            try:
                await self.send_redis_stats()
                await asyncio.sleep(1)  # Update every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in periodic update: {str(e)}")
                break
            
    async def send_redis_stats(self):
        if not self.redis_client:
            return
            
        try:
            info = self.redis_client.info()
            
            # Format memory size
            memory_bytes = info.get('used_memory', 0)
            if memory_bytes < 1024:
                memory = f"{memory_bytes} B"
            elif memory_bytes < 1024 * 1024:
                memory = f"{memory_bytes/1024:.1f} KB"
            else:
                memory = f"{memory_bytes/(1024*1024):.1f} MB"
            
            # Get other stats
            clients = info.get('connected_clients', 0)
            peak_clients = info.get('connected_clients_peak', 0)
            ops_per_sec = info.get('instantaneous_ops_per_sec', 0)
            uptime_seconds = info.get('uptime_in_seconds', 0)
            
            # Format uptime
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60
            uptime = f"{days}d {hours}h {minutes}m"
            
            await self.send(json.dumps({
                'type': 'redis_stats',
                'data': {
                    'memory': memory,
                    'clients': clients,
                    'peak_clients': peak_clients,
                    'ops_per_sec': ops_per_sec,
                    'uptime': uptime
                }
            }))
            
        except redis.ConnectionError:
            await self.send(json.dumps({
                'type': 'redis_status',
                'status': 'disconnected',
                'message': 'Lost connection to Redis server'
            }))
            await self.cleanup()
                
        except Exception as e:
            print(f"Error getting Redis stats: {str(e)}")
            await self.send(json.dumps({
                'type': 'redis_status',
                'status': 'error',
                'message': f'Error getting Redis stats: {str(e)}'
            }))

class SystemStatsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.update_task = asyncio.create_task(self.send_stats())

    async def disconnect(self, close_code):
        if hasattr(self, 'update_task'):
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass

    async def send_stats(self):
        while True:
            try:
                # Get CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                
                # Get memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Get disk usage
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                
                # Get active tasks (processes)
                active_tasks = len(psutil.Process().children())
                
                await self.send(json.dumps({
                    'type': 'system_stats',
                    'data': {
                        'cpu_percent': round(cpu_percent, 1),
                        'memory_percent': round(memory_percent, 1),
                        'disk_percent': round(disk_percent, 1),
                        'active_tasks': active_tasks
                    }
                }))
                
                # Update performance metrics
                await self.send(json.dumps({
                    'type': 'performance_metrics',
                    'data': {
                        'cpu_usage': round(cpu_percent, 1),
                        'memory_usage': round(memory_percent, 1),
                        'active_tasks': active_tasks
                    }
                }))
                
            except Exception as e:
                print(f"Error getting system stats: {str(e)}")
                
            await asyncio.sleep(2)  # Update every 2 seconds
