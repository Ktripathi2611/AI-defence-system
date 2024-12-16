from flask import Blueprint, render_template, jsonify, request, current_app, flash, redirect, url_for, send_from_directory, Response
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
import os
import threading
import time
import re
import psutil
from werkzeug.utils import secure_filename

# Import models
from src.models import db
from src.models.threat_analysis import ThreatAnalysis
from src.models.scan import Scan
from src.models.activity import Activity
from src.models.notifications import Notifications
from src.models.alert import Alert
from src.models.deepfake_analysis import DeepFakeAnalysis
from src.models.system_status import SystemStatus

# Import AI modules
from src.ai_modules.deepfake_detector import analyze_deepfake
from src.ai_modules.threat_analyzer import analyze_threats as analyze_threat
from src.ai_modules.malware_detector import analyze_malware

main_bp = Blueprint('main', __name__)

# Register custom filters
from src.utils.filters import format_number, time_ago

def init_app(app):
    """Initialize the blueprint with the app context"""
    app.jinja_env.filters['format_number'] = format_number
    app.jinja_env.filters['time_ago'] = time_ago

@main_bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Render the main dashboard page."""
    # Get system status
    system_status = SystemStatus.query.first()
    if not system_status:
        system_status = SystemStatus(status='stopped')
        db.session.add(system_status)
        db.session.commit()

    # Get recent threats
    recent_threats = ThreatAnalysis.query.order_by(
        ThreatAnalysis.timestamp.desc()
    ).limit(5).all()
    
    # Get recent scans
    recent_scans = Scan.query.order_by(Scan.timestamp.desc()).limit(5).all()
    
    # Calculate active threats trend
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    
    current_threats = ThreatAnalysis.query.filter(
        ThreatAnalysis.status == 'active'
    ).count()
    
    past_threats = ThreatAnalysis.query.filter(
        ThreatAnalysis.status == 'active',
        ThreatAnalysis.timestamp <= week_ago
    ).count()
    
    if past_threats > 0:
        trend = ((current_threats - past_threats) / past_threats) * 100
    else:
        trend = 0 if current_threats == 0 else 100
    
    # Get system metrics
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    
    # Calculate next scan time (example: every 4 hours)
    scan_interval = timedelta(hours=4)
    last_scan = Scan.query.order_by(Scan.timestamp.desc()).first()
    if last_scan:
        next_scan_time = last_scan.timestamp + scan_interval
    else:
        next_scan_time = datetime.utcnow() + scan_interval
    
    # Maximum scans per day setting
    max_scans = 24  # Example: 24 scans per day (1 per hour)
    
    return render_template('dashboard.html',
                         recent_threats=recent_threats,
                         recent_scans=recent_scans,
                         active_threats=current_threats,
                         trend=trend,
                         cpu_usage=cpu_usage,
                         memory_usage=memory_usage,
                         current_time=datetime.now(),
                         next_scan_time=next_scan_time,
                         max_scans=max_scans,
                         system_status=system_status.status,
                         last_state_change=system_status.last_state_change)

@main_bp.route('/scan')
@login_required
def scan():
    """Render the scan page."""
    recent_scans = Scan.query.order_by(Scan.timestamp.desc()).limit(10).all()
    return render_template('dashboard/scan.html', recent_scans=recent_scans)

@main_bp.route('/alerts')
@login_required
def alerts():
    """Render the alerts page."""
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    return render_template('dashboard/alerts.html', alerts=alerts)

@main_bp.route('/reports')
@login_required
def reports():
    """Render the reports page."""
    return render_template('dashboard/reports.html')

@main_bp.route('/settings')
@login_required
def settings():
    """Render the settings page."""
    return render_template('dashboard/settings.html')

@main_bp.route('/threat-analysis')
@login_required
def threat_analysis():
    """Render the threat analysis page."""
    return render_template('dashboard/threat_analysis.html')

@main_bp.route('/deepfake-detection')
@login_required
def deepfake_detection():
    """Render the deepfake detection page."""
    return render_template('dashboard/deepfake_detection.html')

def extract_threats(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract threats from a scan result safely."""
    if not isinstance(result, dict):
        return []
    return result.get('threats', [])

def perform_scan(file_path: str, filename: str, scan_id: int) -> None:
    """Perform the actual file scanning using AI modules."""
    try:
        # Update scan status to in progress
        scan = Scan.query.get(scan_id)
        if not scan:
            return
        
        scan.status = 'in_progress'
        db.session.commit()

        # Perform various analyses
        threat_result = analyze_threat(file_path)
        malware_result = analyze_malware(file_path)
        deepfake_result = analyze_deepfake(file_path)

        # Extract and combine threats
        threats = (
            extract_threats(threat_result) +
            extract_threats(malware_result) +
            extract_threats(deepfake_result)
        )

        # Create threat analysis records
        for threat in threats:
            analysis = ThreatAnalysis(
                scan_id=scan_id,
                type=threat.get('type', 'unknown'),
                severity=threat.get('severity', 'low'),
                details=threat.get('details', ''),
                status='active'
            )
            db.session.add(analysis)

        # Update scan status
        scan.status = 'completed'
        scan.completion_time = datetime.utcnow()
        db.session.commit()

    except Exception as e:
        current_app.logger.error(f"Error in perform_scan: {str(e)}")
        if scan:
            scan.status = 'error'
            scan.error_message = str(e)
            db.session.commit()

@main_bp.route('/api/scan-file', methods=['POST'])
@login_required
def scan_file():
    """Handle file upload and scanning."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Create scan record
        scan = Scan(
            filename=filename,
            status='pending',
            scan_type='file'
        )
        db.session.add(scan)
        db.session.commit()

        # Start scanning in background
        thread = threading.Thread(
            target=perform_scan,
            args=(file_path, filename, scan.id)
        )
        thread.start()

        return jsonify({
            'message': 'Scan initiated',
            'scan_id': scan.id
        }), 202

    except Exception as e:
        current_app.logger.error(f"Error in scan_file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/scan-url', methods=['POST'])
@login_required
def scan_url():
    """Handle URL scanning."""
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']
    if not url:
        return jsonify({'error': 'Empty URL provided'}), 400

    try:
        # Create scan record
        scan = Scan(
            target_url=url,
            status='pending',
            scan_type='url'
        )
        db.session.add(scan)
        db.session.commit()

        # Start scanning in background
        thread = threading.Thread(
            target=perform_url_scan,
            args=(url, scan.id)
        )
        thread.start()

        return jsonify({
            'message': 'URL scan initiated',
            'scan_id': scan.id
        }), 202

    except Exception as e:
        current_app.logger.error(f"Error in scan_url: {str(e)}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if the file extension is allowed."""
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/api/system/<action>', methods=['POST'])
@login_required
def system_control(action):
    """Handle system start/stop actions"""
    if action not in ['start', 'stop']:
        return jsonify({'status': 'error', 'message': 'Invalid action'}), 400

    try:
        system_status = SystemStatus.query.first()
        if not system_status:
            system_status = SystemStatus(status='stopped')
            db.session.add(system_status)

        # Check if the action matches current state
        if (action == 'start' and system_status.status == 'running') or \
           (action == 'stop' and system_status.status == 'stopped'):
            return jsonify({
                'status': 'error',
                'message': f'System is already {system_status.status}'
            }), 400

        # Update system status
        system_status.status = 'running' if action == 'start' else 'stopped'
        system_status.last_state_change = datetime.utcnow()
        
        # Log the activity
        activity = Activity(
            user_id=current_user.id,
            event=f'System {action}ed',
            status='success',
            details=f'System was successfully {action}ed by {current_user.username}'
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'System {action}ed successfully',
            'system_status': system_status.status,
            'last_state_change': system_status.last_state_change.isoformat()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Failed to {action} system: {str(e)}'
        }), 500

@main_bp.route('/api/system/stats')
@login_required
def system_stats():
    """Get current system statistics"""
    try:
        # Get CPU and memory usage using psutil
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        # Get scan statistics
        active_scans = Scan.query.filter_by(status='in_progress').count()
        total_scans = Scan.query.count()
        today_scans = Scan.query.filter(
            Scan.created_at >= datetime.now().date()
        ).count()

        # Get threat statistics
        threats = ThreatAnalysis.query.all()
        threats_detected = len(threats)
        critical_threats = sum(1 for t in threats if t.severity == 'critical')
        warning_threats = sum(1 for t in threats if t.severity == 'warning')

        return jsonify({
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'active_scans': active_scans,
            'total_scans': total_scans,
            'today_scans': today_scans,
            'threats_detected': threats_detected,
            'critical_threats': critical_threats,
            'warning_threats': warning_threats
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get system stats: {str(e)}'
        }), 500
