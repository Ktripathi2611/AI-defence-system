import asyncio
import datetime
import os
import psutil
import aiohttp
from aiohttp import web
import socketio
import json
import logging
from pathlib import Path

# Initialize Socket.IO
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active monitoring tasks
monitoring_tasks = {}

class SystemMonitor:
    @staticmethod
    def get_system_metrics():
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

    @staticmethod
    def get_network_metrics():
        net_io = psutil.net_io_counters()
        return {
            'upload_speed': net_io.bytes_sent / 1024 / 1024,  # MB/s
            'download_speed': net_io.bytes_recv / 1024 / 1024,  # MB/s
            'total_bandwidth': (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024  # MB/s
        }

    @staticmethod
    def get_process_metrics():
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'] or 0.0,
                    'memory_percent': pinfo['memory_percent'] or 0.0,
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return {'processes': processes[:10]}  # Return top 10 processes

async def monitor_system_resources(sid):
    """Monitor system resources and send updates"""
    try:
        while True:
            metrics = SystemMonitor.get_system_metrics()
            await sio.emit('system_metrics', metrics, room=sid)
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error in system monitoring: {str(e)}")

async def monitor_network(sid):
    """Monitor network activity and send updates"""
    try:
        while True:
            metrics = SystemMonitor.get_network_metrics()
            await sio.emit('network_metrics', metrics, room=sid)
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error in network monitoring: {str(e)}")

async def monitor_processes(sid):
    """Monitor processes and send updates"""
    try:
        while True:
            metrics = SystemMonitor.get_process_metrics()
            await sio.emit('process_metrics', metrics, room=sid)
            await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"Error in process monitoring: {str(e)}")

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")
    # Cancel any monitoring tasks for this client
    if sid in monitoring_tasks:
        for task in monitoring_tasks[sid]:
            task.cancel()
        monitoring_tasks.pop(sid)

@sio.event
async def start_systemResources_monitoring(sid):
    if sid not in monitoring_tasks:
        monitoring_tasks[sid] = []
    task = asyncio.create_task(monitor_system_resources(sid))
    monitoring_tasks[sid].append(task)
    logger.info(f"Started system resources monitoring for {sid}")

@sio.event
async def stop_systemResources_monitoring(sid):
    if sid in monitoring_tasks:
        for task in monitoring_tasks[sid]:
            task.cancel()
        monitoring_tasks[sid] = []
    logger.info(f"Stopped system resources monitoring for {sid}")

@sio.event
async def start_network_monitoring(sid):
    if sid not in monitoring_tasks:
        monitoring_tasks[sid] = []
    task = asyncio.create_task(monitor_network(sid))
    monitoring_tasks[sid].append(task)
    logger.info(f"Started network monitoring for {sid}")

@sio.event
async def stop_network_monitoring(sid):
    if sid in monitoring_tasks:
        for task in monitoring_tasks[sid]:
            task.cancel()
        monitoring_tasks[sid] = []
    logger.info(f"Stopped network monitoring for {sid}")

@sio.event
async def start_processes_monitoring(sid):
    if sid not in monitoring_tasks:
        monitoring_tasks[sid] = []
    task = asyncio.create_task(monitor_processes(sid))
    monitoring_tasks[sid].append(task)
    logger.info(f"Started process monitoring for {sid}")

@sio.event
async def stop_processes_monitoring(sid):
    if sid in monitoring_tasks:
        for task in monitoring_tasks[sid]:
            task.cancel()
        monitoring_tasks[sid] = []
    logger.info(f"Stopped process monitoring for {sid}")

# Routes
async def index(request):
    try:
        with open(Path(__file__).parent / 'templates' / 'security_dashboard.html', 'r') as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
    except Exception as e:
        logger.error(f"Error serving dashboard: {str(e)}")
        return web.Response(text=f"Error: {str(e)}", status=500)

# Setup routes
app.router.add_get('/', index)

if __name__ == '__main__':
    try:
        web.run_app(app, host='127.0.0.1', port=5000)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
