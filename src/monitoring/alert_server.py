import asyncio
import datetime
from typing import Dict, Any, List
import aiohttp
from aiohttp import web
import socketio
from alert_manager import AlertManager, Alert

class AlertServer:
    def __init__(self):
        self.alert_manager = AlertManager()
        self.sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        self.app = web.Application()
        self.sio.attach(self.app)
        self._setup_routes()

    def _setup_routes(self):
        """Setup web routes"""
        self.app.router.add_static('/static', 'src/monitoring/static')
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/alerts', self.alerts_handler)
        self.app.router.add_get('/alerts/active', self.active_alerts_handler)
        self.app.router.add_get('/alerts/history', self.alert_history_handler)

    async def index_handler(self, request: web.Request) -> web.Response:
        """Serve the alert dashboard"""
        try:
            with open('src/monitoring/alert_dashboard.html', 'r') as f:
                content = f.read()
            return web.Response(text=content, content_type='text/html')
        except Exception as e:
            print(f"Error serving dashboard: {str(e)}")
            return web.Response(text=f"Error: {str(e)}", status=500)

    async def alerts_handler(self, request: web.Request) -> web.Response:
        """Get all alerts"""
        try:
            active_alerts = self.alert_manager.get_active_alerts()
            alert_history = self.alert_manager.get_alert_history()
            return web.json_response({
                'active': [self._serialize_alert(a) for a in active_alerts],
                'history': [self._serialize_alert(a) for a in alert_history]
            })
        except Exception as e:
            return web.Response(status=500, text=str(e))

    async def active_alerts_handler(self, request: web.Request) -> web.Response:
        """Get active alerts"""
        try:
            active_alerts = self.alert_manager.get_active_alerts()
            return web.json_response([self._serialize_alert(a) for a in active_alerts])
        except Exception as e:
            return web.Response(status=500, text=str(e))

    async def alert_history_handler(self, request: web.Request) -> web.Response:
        """Get alert history"""
        try:
            limit = int(request.query.get('limit', 50))
            alert_history = self.alert_manager.get_alert_history(limit)
            return web.json_response([self._serialize_alert(a) for a in alert_history])
        except Exception as e:
            return web.Response(status=500, text=str(e))

    def _serialize_alert(self, alert: Alert) -> Dict[str, Any]:
        """Serialize alert object to dictionary"""
        return {
            'id': alert.id,
            'metric': alert.metric,
            'value': alert.value,
            'threshold': alert.threshold,
            'severity': alert.severity,
            'timestamp': alert.timestamp,
            'message': alert.message,
            'acknowledged': alert.acknowledged
        }

    async def broadcast_alert_update(self):
        """Broadcast alert updates to all connected clients"""
        active_alerts = self.alert_manager.get_active_alerts()
        alert_history = self.alert_manager.get_alert_history()
        
        await self.sio.emit('alert_update', {
            'active': [self._serialize_alert(a) for a in active_alerts],
            'history': [self._serialize_alert(a) for a in alert_history]
        })

    @staticmethod
    def _get_time_range(range_str: str) -> datetime.timedelta:
        """Convert time range string to timedelta"""
        ranges = {
            '1h': datetime.timedelta(hours=1),
            '6h': datetime.timedelta(hours=6),
            '24h': datetime.timedelta(days=1),
            '7d': datetime.timedelta(days=7)
        }
        return ranges.get(range_str, datetime.timedelta(hours=1))

    async def handle_socket_events(self):
        @self.sio.event
        async def connect(sid, environ):
            print(f'Client connected: {sid}')
            await self.broadcast_alert_update()

        @self.sio.event
        async def disconnect(sid):
            print(f'Client disconnected: {sid}')

        @self.sio.event
        async def acknowledge_alert(sid, alert_id):
            if self.alert_manager.acknowledge_alert(alert_id):
                await self.broadcast_alert_update()

        @self.sio.event
        async def refresh_alerts(sid):
            await self.broadcast_alert_update()

        @self.sio.event
        async def change_time_range(sid, range_str):
            time_range = self._get_time_range(range_str)
            current_time = datetime.datetime.now()
            start_time = current_time - time_range
            
            # Filter alerts based on time range
            filtered_history = [
                alert for alert in self.alert_manager.get_alert_history()
                if datetime.datetime.fromisoformat(alert.timestamp) >= start_time
            ]
            
            await self.sio.emit('alert_update', {
                'active': [self._serialize_alert(a) for a in self.alert_manager.get_active_alerts()],
                'history': [self._serialize_alert(a) for a in filtered_history]
            }, room=sid)

    async def start(self):
        """Start the alert server"""
        await self.handle_socket_events()  # Changed to await the coroutine
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8081)
        await site.start()
        print("Alert server started on http://localhost:8081")

        # Start periodic alert updates
        while True:
            await self.broadcast_alert_update()
            await asyncio.sleep(5)  # Update every 5 seconds

async def main():
    """Main function to run the alert server"""
    server = AlertServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        print("Shutting down alert server...")

if __name__ == "__main__":
    asyncio.run(main())
