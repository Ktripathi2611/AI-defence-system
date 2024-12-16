from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from ...monitoring.health_check import health_checker
from ...utils.monitoring import MonitoringService
from ...auth.middleware import admin_required, rate_limit

monitoring_bp = Blueprint('monitoring', __name__)
monitoring_service = MonitoringService()

@monitoring_bp.route('/health', methods=['GET'])
@rate_limit(requests_per_minute=60)
def health_check():
    """Basic health check endpoint"""
    return jsonify({'status': 'healthy'})

@monitoring_bp.route('/health/detailed', methods=['GET'])
@jwt_required()
@admin_required()
@rate_limit(requests_per_minute=30)
def detailed_health_check():
    """Detailed system health check for admins"""
    try:
        health_status = health_checker.check_system_health()
        return jsonify(health_status)
    except Exception as e:
        monitoring_service.record_error('detailed_health_check', str(e))
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/metrics', methods=['GET'])
@jwt_required()
@admin_required()
@rate_limit(requests_per_minute=30)
def get_metrics():
    """Get system metrics"""
    try:
        metrics = monitoring_service.get_system_stats()
        return jsonify(metrics)
    except Exception as e:
        monitoring_service.record_error('metrics_fetch', str(e))
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/logs', methods=['GET'])
@jwt_required()
@admin_required()
@rate_limit(requests_per_minute=30)
def get_logs():
    """Get system logs"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        log_type = request.args.get('type', 'all')
        
        logs = monitoring_service.get_logs(
            page=page,
            per_page=per_page,
            log_type=log_type
        )
        
        return jsonify(logs)
    except Exception as e:
        monitoring_service.record_error('logs_fetch', str(e))
        return jsonify({'error': str(e)}), 500

@monitoring_bp.route('/alerts', methods=['GET'])
@jwt_required()
@admin_required()
@rate_limit(requests_per_minute=30)
def get_alerts():
    """Get system alerts"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        severity = request.args.get('severity', None)
        
        alerts = monitoring_service.get_alerts(
            page=page,
            per_page=per_page,
            severity=severity
        )
        
        return jsonify(alerts)
    except Exception as e:
        monitoring_service.record_error('alerts_fetch', str(e))
        return jsonify({'error': str(e)}), 500
