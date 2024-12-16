import asyncio
import datetime
import json
from typing import Dict, Any, List
import psutil
import torch
import aiohttp
from aiohttp import web
import socketio
from dataclasses import dataclass, asdict
import logging
from ..optimization.resource_manager import ResourceManager
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

class RealtimeMonitor:
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.monitoring_service = MonitoringService()
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        self.app = web.Application()
        self.sio.attach(self.app)
        self.metrics_history: List[SystemMetrics] = []
        self.max_history_size = 1000
        self.logger = self._setup_logger()
        self._setup_routes()

    def _setup_logger(self) -> logging.Logger:
        """Initialize logger for monitoring"""
        logger = logging.getLogger('realtime_monitor')
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler('monitor.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _setup_routes(self) -> None:
        """Setup web routes"""
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/metrics', self.metrics_handler)
        self.app.router.add_get('/history', self.history_handler)
        self.app.router.add_get('/stats', self.stats_handler)

    async def index_handler(self, request: web.Request) -> web.Response:
        """Serve the monitoring dashboard"""
        return web.FileResponse('monitoring/dashboard.html')

    async def metrics_handler(self, request: web.Request) -> web.Response:
        """Get current system metrics"""
        try:
            metrics = await self.get_current_metrics()
            return web.json_response(asdict(metrics))
        except Exception as e:
            self.logger.error(f'Error getting metrics: {str(e)}')
            return web.Response(status=500, text=str(e))

    async def history_handler(self, request: web.Request) -> web.Response:
        """Get metrics history"""
        try:
            return web.json_response([asdict(m) for m in self.metrics_history])
        except Exception as e:
            self.logger.error(f'Error getting history: {str(e)}')
            return web.Response(status=500, text=str(e))

    async def stats_handler(self, request: web.Request) -> web.Response:
        """Get system statistics"""
        try:
            stats = await self.get_system_stats()
            return web.json_response(stats)
        except Exception as e:
            self.logger.error(f'Error getting stats: {str(e)}')
            return web.Response(status=500, text=str(e))

    async def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            resource_stats = self.resource_manager.get_resource_stats()
            
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
                error_count=self.monitoring_service.get_error_count()
            )

            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history.pop(0)

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

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            current_metrics = await self.get_current_metrics()
            history = self.metrics_history[-100:]  # Last 100 records

            return {
                'current': asdict(current_metrics),
                'averages': {
                    'cpu': sum(m.cpu_usage for m in history) / len(history),
                    'memory': sum(m.memory_usage for m in history) / len(history),
                    'disk': sum(m.disk_usage for m in history) / len(history)
                },
                'peaks': {
                    'cpu': max(m.cpu_usage for m in history),
                    'memory': max(m.memory_usage for m in history),
                    'disk': max(m.disk_usage for m in history)
                },
                'errors': {
                    'count': current_metrics.error_count,
                    'rate': sum(1 for m in history if m.error_count > 0) / len(history)
                }
            }
        except Exception as e:
            self.logger.error(f'Error getting system stats: {str(e)}')
            raise

    async def broadcast_metrics(self) -> None:
        """Broadcast metrics to all connected clients"""
        while True:
            try:
                metrics = await self.get_current_metrics()
                await self.sio.emit('metrics_update', asdict(metrics))
                await asyncio.sleep(1)  # Update every second
            except Exception as e:
                self.logger.error(f'Error broadcasting metrics: {str(e)}')
                await asyncio.sleep(1)

    @staticmethod
    def format_bytes(bytes: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"

    async def start(self) -> None:
        """Start the monitoring server"""
        try:
            self.logger.info("Starting monitoring server...")
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', 8080)
            await site.start()
            
            # Start broadcasting metrics
            asyncio.create_task(self.broadcast_metrics())
            
            self.logger.info("Monitoring server started on http://localhost:8080")
        except Exception as e:
            self.logger.error(f'Error starting server: {str(e)}')
            raise

    async def shutdown(self) -> None:
        """Shutdown the monitoring server"""
        try:
            self.logger.info("Shutting down monitoring server...")
            await self.sio.disconnect()
            await self.app.shutdown()
            self.logger.info("Monitoring server shutdown complete")
        except Exception as e:
            self.logger.error(f'Error during shutdown: {str(e)}')
            raise

async def main() -> None:
    """Main function to run the monitoring server"""
    monitor = RealtimeMonitor()
    try:
        await monitor.start()
        while True:
            await asyncio.sleep(3600)  # Keep running
    except KeyboardInterrupt:
        await monitor.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
