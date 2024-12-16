import asyncio
import datetime
from typing import Dict, Any, List
import aiohttp
from aiohttp import web
import socketio
from dataclasses import dataclass, asdict
import logging
import psutil
import torch
import json
from ..optimization.resource_manager import ResourceManager
from ..optimization.cache_manager import CacheManager
from ..monitoring.alert_manager import AlertManager
from ..utils.monitoring import MonitoringService

@dataclass
class SystemMetrics:
    timestamp: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: Dict[str, float]
    disk_usage: float
    network_io: Dict[str, int]
    active_tasks: int
    error_count: int
    cache_stats: Dict[str, float]
    threat_stats: Dict[str, int]

class UnifiedDashboard:
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.cache_manager = CacheManager()
        self.alert_manager = AlertManager()
        self.monitoring_service = MonitoringService()
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        self.app = web.Application()
        self.sio.attach(self.app)
        self.logger = self._setup_logger()
        self._setup_routes()

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for unified dashboard"""
        logger = logging.getLogger('unified_dashboard')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('dashboard.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _setup_routes(self):
        """Setup web routes"""
        self.app.router.add_static('/static', 'src/dashboard/static')
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/api/metrics', self.metrics_handler)
        self.app.router.add_get('/api/alerts', self.alerts_handler)
        self.app.router.add_get('/api/threats', self.threats_handler)
        self.app.router.add_get('/api/performance', self.performance_handler)

    async def index_handler(self, request: web.Request) -> web.Response:
        """Serve the unified dashboard"""
        try:
            with open('src/dashboard/templates/unified_dashboard.html', 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except Exception as e:
            self.logger.error(f"Error serving dashboard: {str(e)}")
            return web.Response(text=f"Error: {str(e)}", status=500)

    async def metrics_handler(self, request: web.Request) -> web.Response:
        """Get current system metrics"""
        try:
            metrics = await self.get_current_metrics()
            return web.json_response(asdict(metrics))
        except Exception as e:
            self.logger.error(f'Error getting metrics: {str(e)}')
            return web.Response(status=500, text=str(e))

    async def alerts_handler(self, request: web.Request) -> web.Response:
        """Get system alerts"""
        try:
            active_alerts = self.alert_manager.get_active_alerts()
            alert_history = self.alert_manager.get_alert_history()
            return web.json_response({
                'active': [asdict(a) for a in active_alerts],
                'history': [asdict(a) for a in alert_history]
            })
        except Exception as e:
            self.logger.error(f'Error getting alerts: {str(e)}')
            return web.Response(status=500, text=str(e))

    async def threats_handler(self, request: web.Request) -> web.Response:
        """Get threat statistics"""
        try:
            threats = await self.get_threat_stats()
            return web.json_response(threats)
        except Exception as e:
            self.logger.error(f'Error getting threats: {str(e)}')
            return web.Response(status=500, text=str(e))

    async def performance_handler(self, request: web.Request) -> web.Response:
        """Get performance metrics"""
        try:
            performance = await self.get_performance_stats()
            return web.json_response(performance)
        except Exception as e:
            self.logger.error(f'Error getting performance stats: {str(e)}')
            return web.Response(status=500, text=str(e))

    async def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            resource_stats = self.resource_manager.get_resource_stats()
            cache_stats = self.cache_manager.get_stats()
            threat_stats = await self.get_threat_stats()
            
            metrics = SystemMetrics(
                timestamp=datetime.datetime.now().isoformat(),
                cpu_usage=resource_stats['cpu']['percent'],
                memory_usage=resource_stats['memory']['percent'],
                gpu_usage=self._get_gpu_usage(),
                disk_usage=resource_stats['disk']['percent'],
                network_io={
                    'bytes_sent': resource_stats['network']['bytes_sent'],
                    'bytes_recv': resource_stats['network']['bytes_recv']
                },
                active_tasks=len(self.resource_manager._get_active_tasks()),
                error_count=self.monitoring_service.get_error_count(),
                cache_stats=cache_stats,
                threat_stats=threat_stats
            )
            return metrics
        except Exception as e:
            self.logger.error(f'Error collecting metrics: {str(e)}')
            raise

    def _get_gpu_usage(self) -> Dict[str, float]:
        """Get GPU usage statistics"""
        gpu_stats = {}
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                try:
                    memory = torch.cuda.memory_stats(i)
                    total = torch.cuda.get_device_properties(i).total_memory
                    used = memory.get('allocated_bytes.all.current', 0)
                    gpu_stats[f'gpu_{i}'] = (used / total) * 100
                except Exception as e:
                    self.logger.error(f'Error getting GPU {i} stats: {str(e)}')
                    gpu_stats[f'gpu_{i}'] = 0.0
        return gpu_stats

    async def get_threat_stats(self) -> Dict[str, int]:
        """Get threat statistics"""
        try:
            return {
                'malware': self.monitoring_service.get_threat_count('malware'),
                'deepfake': self.monitoring_service.get_threat_count('deepfake'),
                'phishing': self.monitoring_service.get_threat_count('phishing'),
                'total': self.monitoring_service.get_total_threat_count()
            }
        except Exception as e:
            self.logger.error(f'Error getting threat stats: {str(e)}')
            raise

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        try:
            return {
                'query_performance': self.monitoring_service.get_query_performance(),
                'cache_performance': self.cache_manager.get_performance_stats(),
                'resource_utilization': self.resource_manager.get_utilization_stats()
            }
        except Exception as e:
            self.logger.error(f'Error getting performance stats: {str(e)}')
            raise

    async def broadcast_updates(self):
        """Broadcast updates to all connected clients"""
        while True:
            try:
                # Get all metrics
                metrics = await self.get_current_metrics()
                alerts = self.alert_manager.get_active_alerts()
                performance = await self.get_performance_stats()
                threats = await self.get_threat_stats()

                # Broadcast updates
                await self.sio.emit('metrics_update', asdict(metrics))
                await self.sio.emit('alerts_update', [asdict(a) for a in alerts])
                await self.sio.emit('performance_update', performance)
                await self.sio.emit('threats_update', threats)

                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                self.logger.error(f'Error broadcasting updates: {str(e)}')
                await asyncio.sleep(5)

    async def start(self):
        """Start the unified dashboard"""
        try:
            self.logger.info("Starting unified dashboard...")
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', 8080)
            await site.start()
            
            # Start broadcasting updates
            asyncio.create_task(self.broadcast_updates())
            
            self.logger.info("Unified dashboard started on http://localhost:8080")
        except Exception as e:
            self.logger.error(f'Error starting dashboard: {str(e)}')
            raise

    async def shutdown(self):
        """Shutdown the unified dashboard"""
        try:
            self.logger.info("Shutting down unified dashboard...")
            await self.sio.disconnect()
            await self.app.shutdown()
            self.logger.info("Unified dashboard shutdown complete")
        except Exception as e:
            self.logger.error(f'Error during shutdown: {str(e)}')
            raise

async def main():
    """Main function to run the unified dashboard"""
    dashboard = UnifiedDashboard()
    try:
        await dashboard.start()
        while True:
            await asyncio.sleep(3600)  # Keep running
    except KeyboardInterrupt:
        await dashboard.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
