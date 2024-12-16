from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import db, Notification
from ...utils.monitoring import MonitoringService
from ...auth.middleware import rate_limit

notifications_bp = Blueprint('notifications', __name__)
monitoring = MonitoringService()

@notifications_bp.route('/notifications', methods=['GET'])
@jwt_required()
@rate_limit(requests_per_minute=60)
def get_notifications():
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get paginated notifications
        notifications = Notification.get_user_notifications(
            user_id,
            page=page,
            per_page=per_page
        )
        
        # Get unread count
        unread_count = Notification.get_unread_count(user_id)
        
        return jsonify({
            'notifications': [n.to_dict() for n in notifications.items],
            'unread_count': unread_count,
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': notifications.page
        })
        
    except Exception as e:
        monitoring.record_error('get_notifications', str(e))
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_as_read(notification_id):
    try:
        user_id = get_jwt_identity()
        notification = Notification.query.get_or_404(notification_id)
        
        # Verify ownership
        if notification.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        notification.mark_as_read()
        
        return jsonify({'message': 'Notification marked as read'})
        
    except Exception as e:
        monitoring.record_error('mark_notification_read', str(e))
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/mark-all-read', methods=['POST'])
@jwt_required()
def mark_all_read():
    try:
        user_id = get_jwt_identity()
        
        # Update all unread notifications
        Notification.query.filter_by(
            user_id=user_id,
            read=False
        ).update({'read': True})
        
        db.session.commit()
        
        return jsonify({'message': 'All notifications marked as read'})
        
    except Exception as e:
        monitoring.record_error('mark_all_notifications_read', str(e))
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/settings', methods=['GET', 'PUT'])
@jwt_required()
def notification_settings():
    try:
        user_id = get_jwt_identity()
        
        if request.method == 'GET':
            settings = NotificationSettings.query.filter_by(user_id=user_id).first()
            return jsonify(settings.to_dict() if settings else {})
            
        # Update settings
        data = request.get_json()
        settings = NotificationSettings.query.filter_by(user_id=user_id).first()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            db.session.add(settings)
            
        settings.update_from_dict(data)
        db.session.commit()
        
        return jsonify(settings.to_dict())
        
    except Exception as e:
        monitoring.record_error('notification_settings', str(e))
        return jsonify({'error': str(e)}), 500
