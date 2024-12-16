from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .. import db
from ..models import Scan, ThreatAnalysis, DeepFakeAnalysis, Activity
from ..ai_modules.threat_detector import analyze_threat
from ..ai_modules.deepfake_detector import DeepFakeDetector
import os
from datetime import datetime

security_bp = Blueprint('security', __name__)
deepfake_detector = DeepFakeDetector()

@security_bp.route('/api/scan/threat', methods=['POST'])
@login_required
def scan_threat():
    data = request.get_json()
    target = data.get('target')
    
    if not target:
        return jsonify({'error': 'No target specified'}), 400

    try:
        # Create scan record
        scan = Scan(
            user_id=current_user.id,
            scan_type='threat',
            target=target,
            status='in_progress'
        )
        db.session.add(scan)
        db.session.commit()

        # Perform threat analysis
        threats = analyze_threat(target)
        
        # Record results
        for threat in threats:
            analysis = ThreatAnalysis(
                scan_id=scan.id,
                threat_type=threat['type'],
                confidence=threat['confidence'],
                details=threat['description']
            )
            db.session.add(analysis)

        # Update scan status
        scan.status = 'completed'
        db.session.commit()

        # Log activity
        activity = Activity(
            user_id=current_user.id,
            activity_type='scan',
            description=f'Completed threat scan for {target}'
        )
        db.session.add(activity)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'threats': threats
        })

    except Exception as e:
        current_app.logger.error(f'Error in threat scan: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/api/analyze/deepfake', methods=['POST'])
@login_required
def analyze_deepfake():
    if 'media' not in request.files:
        return jsonify({'error': 'No media file provided'}), 400

    file = request.files['media']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Create scan record
        scan = Scan(
            user_id=current_user.id,
            scan_type='deepfake',
            target=filename,
            status='in_progress'
        )
        db.session.add(scan)
        db.session.commit()

        # Perform deepfake analysis
        analysis_result = deepfake_detector.analyze_media(filepath)
        
        # Record results
        deepfake_analysis = DeepFakeAnalysis(
            scan_id=scan.id,
            media_type=analysis_result['media_type'],
            confidence=analysis_result['confidence'],
            artifacts_detected=str(analysis_result['artifacts'])
        )
        db.session.add(deepfake_analysis)

        # Update scan status
        scan.status = 'completed'
        db.session.commit()

        # Log activity
        activity = Activity(
            user_id=current_user.id,
            activity_type='analysis',
            description=f'Completed deepfake analysis for {filename}'
        )
        db.session.add(activity)
        db.session.commit()

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify({
            'status': 'success',
            'image_confidence': analysis_result.get('image_confidence', 0),
            'video_confidence': analysis_result.get('video_confidence', 0),
            'audio_confidence': analysis_result.get('audio_confidence', 0)
        })

    except Exception as e:
        current_app.logger.error(f'Error in deepfake analysis: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/api/security/status', methods=['GET'])
@login_required
def get_security_status():
    try:
        # Get latest scan
        latest_scan = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.timestamp.desc()).first()
        
        return jsonify({
            'status': 'active',
            'last_scan': latest_scan.timestamp.isoformat() if latest_scan else None,
            'protection_level': 'high',
            'updates_available': False
        })

    except Exception as e:
        current_app.logger.error(f'Error getting security status: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@security_bp.route('/api/activity/recent', methods=['GET'])
@login_required
def get_recent_activity():
    try:
        activities = Activity.query.filter_by(user_id=current_user.id)\
            .order_by(Activity.timestamp.desc())\
            .limit(10)\
            .all()
        
        return jsonify([{
            'type': activity.activity_type,
            'description': activity.description,
            'timestamp': activity.timestamp.isoformat()
        } for activity in activities])

    except Exception as e:
        current_app.logger.error(f'Error getting recent activity: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500
