import psutil
import torch
import threading
import time
from typing import Dict, List, Optional
import logging
from ..utils.monitoring import MonitoringService

class ResourceManager:
    def __init__(self):
        self.monitoring = MonitoringService()
        self.logger = self._setup_logger()
        self.resource_limits = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'gpu_memory_percent': 90
        }
        self._stop_monitoring = False
        self._start_monitoring_thread()

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for resource management"""
        logger = logging.getLogger('resource_manager')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('resource_manager.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _start_monitoring_thread(self) -> None:
        """Start resource monitoring thread"""
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def _monitor_resources(self) -> None:
        """Continuously monitor system resources"""
        while not self._stop_monitoring:
            try:
                stats = self.get_resource_stats()
                self._check_resource_limits(stats)
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self.logger.error(f'Resource monitoring error: {str(e)}')
                time.sleep(5)

    def _check_resource_limits(self, stats: Dict) -> None:
        """Check if resources exceed limits"""
        try:
            # Check CPU usage
            if stats['cpu']['percent'] > self.resource_limits['cpu_percent']:
                self.logger.warning(f"High CPU usage: {stats['cpu']['percent']}%")
                self.monitoring.record_metric('high_cpu_usage', 1)

            # Check memory usage
            if stats['memory']['percent'] > self.resource_limits['memory_percent']:
                self.logger.warning(f"High memory usage: {stats['memory']['percent']}%")
                self.monitoring.record_metric('high_memory_usage', 1)

            # Check GPU memory if available
            if stats['gpu']['available']:
                for device_id, gpu_stats in stats['gpu']['devices'].items():
                    memory_percent = (gpu_stats['memory_used'] / gpu_stats['memory_total']) * 100
                    if memory_percent > self.resource_limits['gpu_memory_percent']:
                        self.logger.warning(f"High GPU memory usage on device {device_id}: {memory_percent}%")
                        self.monitoring.record_metric('high_gpu_usage', 1)

        except Exception as e:
            self.logger.error(f'Resource limit check failed: {str(e)}')
            self.monitoring.record_error('resource_check', str(e))

    def get_resource_stats(self) -> Dict:
        """Get current resource statistics"""
        try:
            stats = {
                'cpu': self._get_cpu_stats(),
                'memory': self._get_memory_stats(),
                'disk': self._get_disk_stats(),
                'gpu': self._get_gpu_stats(),
                'network': self._get_network_stats()
            }
            
            # Record metrics
            self.monitoring.record_metric('cpu_usage', stats['cpu']['percent'])
            self.monitoring.record_metric('memory_usage', stats['memory']['percent'])
            
            return stats
        except Exception as e:
            self.logger.error(f'Failed to get resource stats: {str(e)}')
            self.monitoring.record_error('resource_stats', str(e))
            return {}

    def _get_cpu_stats(self) -> Dict:
        """Get CPU statistics"""
        cpu_times = psutil.cpu_times()
        return {
            'percent': psutil.cpu_percent(interval=1),
            'cores': psutil.cpu_count(),
            'load_avg': psutil.getloadavg(),
            'times': {
                'user': cpu_times.user,
                'system': cpu_times.system,
                'idle': cpu_times.idle
            }
        }

    def _get_memory_stats(self) -> Dict:
        """Get memory statistics"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap': {
                'total': swap.total,
                'used': swap.used,
                'percent': swap.percent
            }
        }

    def _get_disk_stats(self) -> Dict:
        """Get disk statistics"""
        disk = psutil.disk_usage('/')
        io = psutil.disk_io_counters()
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent,
            'io': {
                'read_bytes': io.read_bytes,
                'write_bytes': io.write_bytes,
                'read_count': io.read_count,
                'write_count': io.write_count
            }
        }

    def _get_gpu_stats(self) -> Dict:
        """Get GPU statistics"""
        if not torch.cuda.is_available():
            return {'available': False}

        devices = {}
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            memory = torch.cuda.memory_stats(i)
            devices[i] = {
                'name': props.name,
                'memory_total': props.total_memory,
                'memory_used': memory.get('allocated_bytes.all.current', 0),
                'memory_free': props.total_memory - memory.get('allocated_bytes.all.current', 0),
                'compute_capability': f"{props.major}.{props.minor}"
            }

        return {
            'available': True,
            'device_count': torch.cuda.device_count(),
            'devices': devices
        }

    def _get_network_stats(self) -> Dict:
        """Get network statistics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'connections': len(psutil.net_connections())
        }

    def optimize_resources(self) -> List[str]:
        """Optimize system resources"""
        try:
            recommendations = []
            stats = self.get_resource_stats()

            # CPU optimization
            if stats['cpu']['percent'] > 70:
                recommendations.append("Consider scaling up CPU resources")

            # Memory optimization
            if stats['memory']['percent'] > 80:
                recommendations.append("Memory usage is high, consider cleanup or scaling")

            # GPU optimization
            if stats['gpu']['available']:
                for device_id, gpu_stats in stats['gpu']['devices'].items():
                    memory_used_percent = (gpu_stats['memory_used'] / gpu_stats['memory_total']) * 100
                    if memory_used_percent > 80:
                        recommendations.append(f"High GPU memory usage on device {device_id}")

            # Disk optimization
            if stats['disk']['percent'] > 85:
                recommendations.append("Disk space is running low, consider cleanup")

            return recommendations
        except Exception as e:
            self.logger.error(f'Resource optimization failed: {str(e)}')
            self.monitoring.record_error('resource_optimization', str(e))
            return []

    def shutdown(self) -> None:
        """Shutdown resource manager"""
        try:
            self._stop_monitoring = True
            if self.monitor_thread:
                self.monitor_thread.join()
            self.logger.info('Resource manager shutdown complete')
        except Exception as e:
            self.logger.error(f'Shutdown error: {str(e)}')
            self.monitoring.record_error('shutdown', str(e))
