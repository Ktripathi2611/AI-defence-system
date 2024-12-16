from datetime import datetime
from src import db

class DeepFakeAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    confidence_score = db.Column(db.Float)  # 0-1 probability of being a deepfake
    detection_method = db.Column(db.String(50))
    artifacts_detected = db.Column(db.JSON)  # List of detected artifacts/anomalies
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_duration = db.Column(db.Float)  # Duration in seconds
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'confidence_score': self.confidence_score,
            'detection_method': self.detection_method,
            'artifacts_detected': self.artifacts_detected,
            'timestamp': self.timestamp.isoformat(),
            'analysis_duration': self.analysis_duration
        }
