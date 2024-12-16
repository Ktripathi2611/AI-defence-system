from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from .. import db
from ..models import Alert, ThreatAnalysis
from ..ai_modules.threat_detector import ThreatDetector
from ..ai_modules.deepfake_detector import DeepFakeDetector

api_bp = Blueprint('api', __name__)
threat_detector = ThreatDetector()
deepfake_detector = DeepFakeDetector()

@api_bp.route('/analyze/bulk', methods=['POST'])
@login_required
def analyze_bulk():
    """Bulk analysis endpoint for multiple URLs or text content"""
    data = request.json
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Invalid data format'}), 400
    
    results = []
    for item in data:
        if 'type' not in item or 'content' not in item:
            continue
        
        if item['type'] == 'url':
            analysis = threat_detector.analyze_url(item['content'])
        elif item['type'] == 'text':
            analysis = threat_detector.analyze_text(item['content'])
        elif item['type'] == 'email':
            analysis = threat_detector.analyze_email(item['content'])
        else:
            continue
        
        results.append({
            'content': item['content'],
            'type': item['type'],
            'analysis': analysis
        })
    
    return jsonify(results)

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get user's threat detection statistics"""
    total_alerts = Alert.query.filter_by(user_id=current_user.id).count()
    resolved_alerts = Alert.query.filter_by(user_id=current_user.id, status='resolved').count()
    false_positives = Alert.query.filter_by(user_id=current_user.id, status='false_positive').count()
    
    threat_types = db.session.query(
        Alert.type,
        db.func.count(Alert.id)
    ).filter_by(user_id=current_user.id).group_by(Alert.type).all()
    
    return jsonify({
        'total_alerts': total_alerts,
        'resolved_alerts': resolved_alerts,
        'false_positives': false_positives,
        'threat_types': dict(threat_types)
    })

@api_bp.route('/reports/summary', methods=['GET'])
@login_required
def get_reports_summary():
    """Get summary of user's threat reports"""
    reports = ThreatAnalysis.query.filter_by(reported_by=current_user.id).all()
    
    summary = {
        'total_reports': len(reports),
        'verified_reports': sum(1 for r in reports if r.verified),
        'threat_types': {}
    }
    
    for report in reports:
        if report.threat_type in summary['threat_types']:
            summary['threat_types'][report.threat_type] += 1
        else:
            summary['threat_types'][report.threat_type] = 1
    
    return jsonify(summary)

@api_bp.route('/deepfake/history', methods=['GET'])
@login_required
def get_deepfake_history():
    """Get user's deepfake analysis history"""
    analyses = DeepFakeAnalysis.query.filter_by(user_id=current_user.id)\
        .order_by(DeepFakeAnalysis.analysis_timestamp.desc()).all()
    
    return jsonify([{
        'id': analysis.id,
        'media_type': analysis.media_type,
        'authenticity_score': analysis.authenticity_score,
        'timestamp': analysis.analysis_timestamp.isoformat(),
        'details': analysis.details
    } for analysis in analyses])

@api_bp.route('/alerts/export', methods=['GET'])
@login_required
def export_alerts():
    """Export user's alerts in JSON format"""
    alerts = Alert.query.filter_by(user_id=current_user.id).all()
    
    return jsonify([{
        'id': alert.id,
        'type': alert.type,
        'content': alert.content,
        'confidence_score': alert.confidence_score,
        'timestamp': alert.timestamp.isoformat(),
        'status': alert.status
    } for alert in alerts])

@api_bp.route('/community/threats', methods=['GET'])
@login_required
def get_community_threats():
    """Get recent community-reported threats"""
    reports = ThreatAnalysis.query.filter_by(verified=True)\
        .order_by(ThreatAnalysis.timestamp.desc())\
        .limit(100).all()
    
    return jsonify([{
        'threat_type': report.threat_type,
        'timestamp': report.timestamp.isoformat(),
        'details': report.details
    } for report in reports])
