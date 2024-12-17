import json
from channels.generic.websocket import AsyncWebsocketConsumer
from celery.events.state import State
from datetime import datetime

class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "task_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "task_updates",
            self.channel_name
        )

    async def system_update(self, event):
        # Send system stats update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'system_update',
            'stats': event['stats']
        }))

    async def task_update(self, event):
        # Send task update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'task_update',
            'stats': event['stats'],
            'task': event.get('task')
        }))

    async def worker_status(self, event):
        # Send worker status update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'worker_status',
            'online': event['online']
        }))
