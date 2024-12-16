from datetime import datetime
from src import db

class ThreatAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    threat_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, resolved
    resolution_notes = db.Column(db.Text)
    resolved_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'resolution_notes': self.resolution_notes,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }
