import logging
from prometheus_client import Counter, Histogram
import time
from datetime import datetime

# Prometheus metrics
SCAN_COUNTER = Counter('file_scans_total', 'Total number of file scans')
SCAN_DURATION = Histogram('scan_duration_seconds', 'Time spent scanning files')
THREAT_COUNTER = Counter('threats_detected_total', 'Total number of threats detected')
LOGIN_COUNTER = Counter('user_logins_total', 'Total number of user logins')
ERROR_COUNTER = Counter('errors_total', 'Total number of errors')

class MonitoringService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
    
    def record_scan(self, scan_type, duration, threats_found):
        SCAN_COUNTER.labels(type=scan_type).inc()
        SCAN_DURATION.observe(duration)
        THREAT_COUNTER.inc(len(threats_found))
        
        self.logger.info(
            f"Scan completed - Type: {scan_type}, Duration: {duration:.2f}s, "
            f"Threats: {len(threats_found)}"
        )
    
    def record_error(self, error_type, error_message):
        ERROR_COUNTER.labels(type=error_type).inc()
        self.logger.error(f"Error occurred - Type: {error_type}, Message: {error_message}")
    
    def record_login(self, username, success=True):
        LOGIN_COUNTER.labels(success=success).inc()
        if success:
            self.logger.info(f"Successful login - User: {username}")
        else:
            self.logger.warning(f"Failed login attempt - User: {username}")
    
    def get_system_stats(self):
        return {
            'total_scans': SCAN_COUNTER._value.get(),
            'total_threats': THREAT_COUNTER._value.get(),
            'average_scan_duration': SCAN_DURATION._sum.get() / max(SCAN_DURATION._count.get(), 1),
            'total_errors': ERROR_COUNTER._value.get()
        }
