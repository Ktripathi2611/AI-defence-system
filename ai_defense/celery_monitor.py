from celery import Celery
from celery.events.receiver import EventReceiver
from celery.events.state import State
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
import json
import threading
import time
import psutil
import redis

def monitor_celery_events():
    app = Celery()
    state = State()
    channel_layer = get_channel_layer()
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def get_system_stats():
        try:
            redis_status = 'online' if redis_client.ping() else 'offline'
        except:
            redis_status = 'offline'

        return {
            'redis': {'status': redis_status},
            'cpu': psutil.cpu_percent(),
            'memory': psutil.virtual_memory().percent
        }

    def get_task_stats(state):
        active = len(state.active())
        completed = len([t for t in state.tasks.values() if t.state == 'SUCCESS'])
        failed = len([t for t in state.tasks.values() if t.state == 'FAILURE'])
        
        return {
            'active': active,
            'completed': completed,
            'failed': failed
        }

    def format_task(task):
        return {
            'name': task.name,
            'status': task.state,
            'started': task.received and datetime.fromtimestamp(task.received).strftime('%H:%M:%S'),
            'duration': task.runtime if task.runtime is not None else '-'
        }

    def send_system_update():
        stats = get_system_stats()
        async_to_sync(channel_layer.group_send)(
            'task_updates',
            {
                'type': 'system_update',
                'stats': stats
            }
        )

    def on_event(event):
        state.event(event)
        if event['type'].startswith('task-'):
            task = state.tasks.get(event['uuid'])
            if task:
                task_stats = get_task_stats(state)
                system_stats = get_system_stats()
                stats = {**task_stats, **system_stats}
                
                async_to_sync(channel_layer.group_send)(
                    'task_updates',
                    {
                        'type': 'task_update',
                        'stats': stats,
                        'task': format_task(task)
                    }
                )

        if event['type'] == 'worker-heartbeat':
            async_to_sync(channel_layer.group_send)(
                'task_updates',
                {
                    'type': 'worker_status',
                    'online': True
                }
            )

    # Start system stats update thread
    def update_system_stats():
        while True:
            try:
                send_system_update()
            except Exception as e:
                print(f"Error updating system stats: {e}")
            time.sleep(5)  # Update every 5 seconds

    system_thread = threading.Thread(target=update_system_stats, daemon=True)
    system_thread.start()

    while True:
        try:
            with app.connection() as connection:
                recv = EventReceiver(
                    connection,
                    handlers={'*': on_event},
                    app=app
                )
                recv.capture(limit=None, timeout=None, wakeup=True)
        except Exception as e:
            print(f"Error capturing events: {e}")
            async_to_sync(channel_layer.group_send)(
                'task_updates',
                {
                    'type': 'worker_status',
                    'online': False
                }
            )
            time.sleep(5)  # Wait before reconnecting

def start_monitor():
    thread = threading.Thread(target=monitor_celery_events, daemon=True)
    thread.start()
    return thread
