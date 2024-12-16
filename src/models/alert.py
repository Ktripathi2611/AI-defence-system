from datetime import datetime
from src.models import db

class Alert(db.Model):
    __tablename__ = 'alert'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    threat_id = db.Column(db.Integer, db.ForeignKey('threat_analysis.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')
    alert_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    scan = db.relationship('Scan', backref='alerts')
    threat = db.relationship('ThreatAnalysis', backref='related_alerts')

    def __init__(self, scan_id, title, description, alert_type, severity='medium', threat_id=None):
        self.scan_id = scan_id
        self.title = title
        self.description = description
        self.alert_type = alert_type
        self.severity = severity
        self.threat_id = threat_id
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'threat_id': self.threat_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'alert_type': self.alert_type,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by
        }

    def __repr__(self):
        return f'<Alert {self.title} - {self.severity}>'
