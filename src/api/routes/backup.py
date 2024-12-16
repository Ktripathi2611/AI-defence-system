from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from ...backup.backup_manager import BackupManager
from ...backup.scheduler import BackupScheduler
from ...auth.middleware import admin_required, rate_limit
from ...utils.monitoring import MonitoringService

backup_bp = Blueprint('backup', __name__)
backup_manager = BackupManager()
backup_scheduler = BackupScheduler()
monitoring = MonitoringService()

@backup_bp.route('/backup/manual', methods=['POST'])
@jwt_required()
@admin_required()
@rate_limit(requests_per_minute=2)
def trigger_manual_backup():
    """Trigger a manual backup"""
    try:
        backup_type = request.json.get('type', 'full')
        
        if backup_type == 'full':
            results = backup_manager.perform_full_backup()
        elif backup_type == 'database':
            db_backup_path = backup_manager.create_database_backup()
            results = {'database': bool(db_backup_path)}
        elif backup_type == 'models':
            model_backups = backup_manager.backup_ai_models()
            results = {'models': bool(model_backups)}
        else:
            return jsonify({'error': 'Invalid backup type'}), 400
            
        return jsonify({
            'message': 'Backup completed successfully',
            'results': results
        })
        
    except Exception as e:
        monitoring.record_error('manual_backup', str(e))
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/backup/schedule', methods=['POST'])
@jwt_required()
@admin_required()
def schedule_backup():
    """Schedule a new backup job"""
    try:
        data = request.get_json()
        job_id = backup_scheduler.add_custom_backup_job(
            func=backup_manager.perform_full_backup,
            trigger=data['trigger'],
            **data.get('trigger_args', {})
        )
        
        if job_id:
            return jsonify({
                'message': 'Backup job scheduled successfully',
                'job_id': job_id
            })
        return jsonify({'error': 'Failed to schedule backup job'}), 500
        
    except Exception as e:
        monitoring.record_error('schedule_backup', str(e))
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/backup/jobs', methods=['GET'])
@jwt_required()
@admin_required()
def list_backup_jobs():
    """List all scheduled backup jobs"""
    try:
        jobs = backup_scheduler.list_all_jobs()
        return jsonify({'jobs': jobs})
    except Exception as e:
        monitoring.record_error('list_backup_jobs', str(e))
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/backup/jobs/<job_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_backup_job(job_id):
    """Get status of a specific backup job"""
    try:
        status = backup_scheduler.get_job_status(job_id)
        if status:
            return jsonify(status)
        return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        monitoring.record_error('get_backup_job', str(e))
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/backup/jobs/<job_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def remove_backup_job(job_id):
    """Remove a scheduled backup job"""
    try:
        if backup_scheduler.remove_backup_job(job_id):
            return jsonify({'message': 'Backup job removed successfully'})
        return jsonify({'error': 'Failed to remove backup job'}), 500
    except Exception as e:
        monitoring.record_error('remove_backup_job', str(e))
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/backup/jobs/<job_id>/pause', methods=['POST'])
@jwt_required()
@admin_required()
def pause_backup_job(job_id):
    """Pause a backup job"""
    try:
        if backup_scheduler.pause_job(job_id):
            return jsonify({'message': 'Backup job paused successfully'})
        return jsonify({'error': 'Failed to pause backup job'}), 500
    except Exception as e:
        monitoring.record_error('pause_backup_job', str(e))
        return jsonify({'error': str(e)}), 500

@backup_bp.route('/backup/jobs/<job_id>/resume', methods=['POST'])
@jwt_required()
@admin_required()
def resume_backup_job(job_id):
    """Resume a paused backup job"""
    try:
        if backup_scheduler.resume_job(job_id):
            return jsonify({'message': 'Backup job resumed successfully'})
        return jsonify({'error': 'Failed to resume backup job'}), 500
    except Exception as e:
        monitoring.record_error('resume_backup_job', str(e))
        return jsonify({'error': str(e)}), 500
