from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from ..models import User, Notification
from ..utils.monitoring import MonitoringService
import json

socketio = SocketIO()
monitoring = MonitoringService()

class NotificationService:
    def __init__(self):
        self.connected_users = {}
    
    def emit_notification(self, user_id, notification_type, data):
        """Emit notification to specific user"""
        if user_id in self.connected_users:
            room = f'user_{user_id}'
            notification = {
                'type': notification_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            }
            socketio.emit('notification', notification, room=room)
            
            # Store notification in database
            self._store_notification(user_id, notification_type, data)
    
    def broadcast_threat_alert(self, threat_data):
        """Broadcast threat alert to all admin users"""
        admin_users = User.query.filter_by(role='admin').all()
        for admin in admin_users:
            self.emit_notification(
                admin.id,
                'threat_alert',
                threat_data
            )
    
    def _store_notification(self, user_id, notification_type, data):
        """Store notification in database"""
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                data=data
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            monitoring.record_error('notification_storage', str(e))

notification_service = NotificationService()

@socketio.on('connect')
def handle_connect():
    try:
        # Get token from query string
        token = request.args.get('token')
        if not token:
            return False
            
        # Verify token and get user
        decoded = decode_token(token)
        user_id = decoded['sub']
        user = User.query.get(user_id)
        
        if not user:
            return False
            
        # Add user to their personal room
        room = f'user_{user_id}'
        join_room(room)
        notification_service.connected_users[user_id] = request.sid
        
        monitoring.logger.info(f"User {user_id} connected to WebSocket")
        return True
        
    except Exception as e:
        monitoring.record_error('websocket_connect', str(e))
        return False

@socketio.on('disconnect')
def handle_disconnect():
    try:
        # Get token from query string
        token = request.args.get('token')
        if token:
            decoded = decode_token(token)
            user_id = decoded['sub']
            
            # Remove user from their room
            room = f'user_{user_id}'
            leave_room(room)
            
            if user_id in notification_service.connected_users:
                del notification_service.connected_users[user_id]
                
            monitoring.logger.info(f"User {user_id} disconnected from WebSocket")
            
    except Exception as e:
        monitoring.record_error('websocket_disconnect', str(e))

@socketio.on_error()
def error_handler(e):
    monitoring.record_error('websocket_error', str(e))
