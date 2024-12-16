from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ...load_balancer.balancer import LoadBalancer
from ...auth.middleware import admin_required, rate_limit
from ...utils.monitoring import MonitoringService

lb_bp = Blueprint('load_balancer', __name__)
load_balancer = LoadBalancer()
monitoring = MonitoringService()

@lb_bp.route('/worker/register', methods=['POST'])
@rate_limit(requests_per_minute=60)
def register_worker():
    """Register a new worker node"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        capabilities = data.get('capabilities', {})

        if not worker_id:
            return jsonify({'error': 'Worker ID is required'}), 400

        if load_balancer.register_worker(worker_id, capabilities):
            return jsonify({
                'message': 'Worker registered successfully',
                'worker_id': worker_id
            })
        return jsonify({'error': 'Failed to register worker'}), 500

    except Exception as e:
        monitoring.record_error('worker_registration', str(e))
        return jsonify({'error': str(e)}), 500

@lb_bp.route('/worker/heartbeat', methods=['POST'])
def worker_heartbeat():
    """Handle worker heartbeat"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')
        status = data.get('status', {})

        if not worker_id:
            return jsonify({'error': 'Worker ID is required'}), 400

        if load_balancer.update_worker_status(worker_id, status):
            return jsonify({'message': 'Heartbeat received'})
        return jsonify({'error': 'Worker not found'}), 404

    except Exception as e:
        monitoring.record_error('worker_heartbeat', str(e))
        return jsonify({'error': str(e)}), 500

@lb_bp.route('/task/assign', methods=['POST'])
@jwt_required()
@rate_limit(requests_per_minute=100)
def assign_task():
    """Assign task to worker"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        requirements = data.get('requirements', {})

        if not task_id:
            return jsonify({'error': 'Task ID is required'}), 400

        worker_id = load_balancer.select_worker(requirements)
        if not worker_id:
            return jsonify({'error': 'No suitable worker available'}), 503

        if load_balancer.assign_task(task_id, worker_id):
            return jsonify({
                'message': 'Task assigned successfully',
                'worker_id': worker_id
            })
        return jsonify({'error': 'Failed to assign task'}), 500

    except Exception as e:
        monitoring.record_error('task_assignment', str(e))
        return jsonify({'error': str(e)}), 500

@lb_bp.route('/task/complete', methods=['POST'])
def complete_task():
    """Mark task as completed"""
    try:
        data = request.get_json()
        task_id = data.get('task_id')
        worker_id = data.get('worker_id')
        status = data.get('status', 'completed')

        if not all([task_id, worker_id]):
            return jsonify({'error': 'Task ID and Worker ID are required'}), 400

        if load_balancer.complete_task(task_id, worker_id, status):
            return jsonify({'message': 'Task marked as completed'})
        return jsonify({'error': 'Failed to complete task'}), 500

    except Exception as e:
        monitoring.record_error('task_completion', str(e))
        return jsonify({'error': str(e)}), 500

@lb_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required()
def get_stats():
    """Get load balancer statistics"""
    try:
        stats = load_balancer.get_worker_stats()
        return jsonify(stats)
    except Exception as e:
        monitoring.record_error('stats_retrieval', str(e))
        return jsonify({'error': str(e)}), 500

@lb_bp.route('/worker/shutdown', methods=['POST'])
def worker_shutdown():
    """Handle worker shutdown"""
    try:
        data = request.get_json()
        worker_id = data.get('worker_id')

        if not worker_id:
            return jsonify({'error': 'Worker ID is required'}), 400

        # Update worker status to inactive
        status = {'status': 'inactive', 'current_load': 0}
        if load_balancer.update_worker_status(worker_id, status):
            return jsonify({'message': 'Worker shutdown acknowledged'})
        return jsonify({'error': 'Worker not found'}), 404

    except Exception as e:
        monitoring.record_error('worker_shutdown', str(e))
        return jsonify({'error': str(e)}), 500
