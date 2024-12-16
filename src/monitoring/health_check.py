import psutil
import torch
import redis
from flask import current_app
from datetime import datetime
import subprocess
from ..utils.monitoring import MonitoringService

monitoring = MonitoringService()

class SystemHealthCheck:
    def __init__(self):
        self.redis_client = current_app.extensions.get('redis')
    
    def check_system_health(self):
        """Perform comprehensive system health check"""
        try:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'system': self._check_system_resources(),
                'gpu': self._check_gpu_status(),
                'services': self._check_services_status(),
                'database': self._check_database(),
                'redis': self._check_redis(),
                'ai_models': self._check_ai_models()
            }
        except Exception as e:
            monitoring.record_error('health_check', str(e))
            return {'error': str(e)}
    
    def _check_system_resources(self):
        """Check CPU, memory, and disk usage"""
        return {
            'cpu': {
                'usage_percent': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count(),
                'load_avg': psutil.getloadavg()
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            }
        }
    
    def _check_gpu_status(self):
        """Check GPU status and memory usage"""
        if not torch.cuda.is_available():
            return {'available': False}
            
        return {
            'available': True,
            'device_count': torch.cuda.device_count(),
            'current_device': torch.cuda.current_device(),
            'device_name': torch.cuda.get_device_name(),
            'memory': {
                'allocated': torch.cuda.memory_allocated(),
                'cached': torch.cuda.memory_cached()
            }
        }
    
    def _check_services_status(self):
        """Check status of critical services"""
        services = {
            'celery': self._check_process('celery'),
            'redis': self._check_process('redis-server'),
            'postgresql': self._check_process('postgres')
        }
        
        # Check web server status
        try:
            response = requests.get(f"{current_app.config['SERVER_NAME']}/health")
            services['web_server'] = {
                'status': 'running' if response.status_code == 200 else 'error',
                'response_time': response.elapsed.total_seconds()
            }
        except:
            services['web_server'] = {'status': 'error'}
        
        return services
    
    def _check_process(self, process_name):
        """Check if a process is running"""
        try:
            subprocess.check_output(['pgrep', '-f', process_name])
            return {'status': 'running'}
        except:
            return {'status': 'stopped'}
    
    def _check_database(self):
        """Check database connection and performance"""
        try:
            start_time = datetime.utcnow()
            db.session.execute('SELECT 1')
            end_time = datetime.utcnow()
            
            return {
                'status': 'connected',
                'response_time': (end_time - start_time).total_seconds(),
                'connection_pool': {
                    'size': db.engine.pool.size(),
                    'checked_out': db.engine.pool.checkedout()
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_redis(self):
        """Check Redis connection and memory usage"""
        try:
            info = self.redis_client.info()
            return {
                'status': 'connected',
                'version': info['redis_version'],
                'memory': {
                    'used': info['used_memory'],
                    'peak': info['used_memory_peak']
                },
                'clients': info['connected_clients'],
                'uptime': info['uptime_in_seconds']
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_ai_models(self):
        """Check AI models status and performance"""
        models = {
            'deepfake_detector': self._check_model_status('deepfake_detector'),
            'malware_analyzer': self._check_model_status('malware_analyzer')
        }
        return models
    
    def _check_model_status(self, model_name):
        """Check individual model status"""
        try:
            model_path = current_app.config[f'{model_name.upper()}_PATH']
            last_modified = datetime.fromtimestamp(os.path.getmtime(model_path))
            
            return {
                'status': 'loaded',
                'last_modified': last_modified.isoformat(),
                'file_size': os.path.getsize(model_path)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

health_checker = SystemHealthCheck()
