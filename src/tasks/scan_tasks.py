from celery import shared_task
from ..models import db, Scan
from ..ai_modules.threat.detector import ThreatDetector
from ..utils.monitoring import MonitoringService
import time

monitoring = MonitoringService()
threat_detector = ThreatDetector()

@shared_task(bind=True, max_retries=3)
def process_scan(self, scan_id, file_path):
    try:
        # Get scan record
        scan = Scan.query.get(scan_id)
        if not scan:
            raise ValueError(f"Scan record {scan_id} not found")
            
        start_time = time.time()
        
        # Run threat analysis
        results = threat_detector.analyze_threat(file_path)
        
        # Calculate overall threat level
        threat_level = results.get('threat_level', 0)
        
        # Update scan record
        scan.status = 'completed'
        scan.threat_level = threat_level
        scan.results = results
        scan.completed_at = time.time()
        
        db.session.commit()
        
        # Record metrics
        duration = time.time() - start_time
        monitoring.record_scan(
            scan_type=scan.file_type,
            duration=duration,
            threats_found=results.get('threats_found', [])
        )
        
        monitoring.logger.info(
            f"Scan completed - ID: {scan_id}, "
            f"Threat Level: {threat_level}%, "
            f"Duration: {duration:.2f}s"
        )
        
        return results
        
    except Exception as e:
        monitoring.record_error('scan_processing', str(e))
        
        # Update scan record with error
        scan = Scan.query.get(scan_id)
        if scan:
            scan.status = 'error'
            scan.error = str(e)
            db.session.commit()
            
        # Retry the task
        raise self.retry(exc=e, countdown=60)  # Retry after 60 seconds
