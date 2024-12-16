from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ...models import db, Scan
from ...ai_modules.threat.detector import ThreatDetector
from ...utils.monitoring import MonitoringService
from ...tasks.scan_tasks import process_scan
import magic

scan_bp = Blueprint('scan', __name__)
monitoring = MonitoringService()
threat_detector = ThreatDetector()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@scan_bp.route('/scan', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'error': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
        
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Check file type using python-magic
        file_type = magic.from_file(file_path, mime=True)
        
        # Create scan record
        scan = Scan(
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            status='processing',
            timestamp=datetime.utcnow()
        )
        db.session.add(scan)
        db.session.commit()
        
        # Start async processing
        process_scan.delay(scan.id, file_path)
        
        monitoring.logger.info(f"File scan initiated - ID: {scan.id}, File: {filename}")
        
        return jsonify({
            'scan_id': scan.id,
            'status': 'processing',
            'message': 'File uploaded and processing started'
        })
        
    except Exception as e:
        monitoring.record_error('scan_upload', str(e))
        return jsonify({'error': str(e)}), 500

@scan_bp.route('/scan/<int:scan_id>', methods=['GET'])
def get_scan_status(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    return jsonify(scan.to_dict())

@scan_bp.route('/scans', methods=['GET'])
def get_scans():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    scans = Scan.query.order_by(Scan.timestamp.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'scans': [scan.to_dict() for scan in scans.items],
        'total': scans.total,
        'pages': scans.pages,
        'current_page': scans.page
    })

@scan_bp.route('/metrics/threats', methods=['GET'])
def get_threat_metrics():
    try:
        # Get threat statistics
        total_threats = Scan.query.filter(Scan.threat_level > 0).count()
        
        # Get threat distribution over time
        threat_distribution = db.session.query(
            Scan.timestamp,
            db.func.count(Scan.id).label('count'),
            db.func.avg(Scan.threat_level).label('avg_threat_level')
        ).group_by(
            db.func.date_trunc('hour', Scan.timestamp)
        ).order_by(Scan.timestamp.desc()).limit(24).all()
        
        distribution_data = [{
            'timestamp': entry.timestamp.isoformat(),
            'count': entry.count,
            'avg_threat_level': float(entry.avg_threat_level)
        } for entry in threat_distribution]
        
        return jsonify({
            'total_threats': total_threats,
            'threat_distribution': distribution_data,
            'updated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        monitoring.record_error('metrics_fetch', str(e))
        return jsonify({'error': str(e)}), 500
