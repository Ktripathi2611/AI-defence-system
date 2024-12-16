from datetime import datetime
from src.models import db
from src.models.alert import Alert

class ThreatAnalysis(db.Model):
    __tablename__ = 'threat_analysis'

    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # malware, deepfake, phishing, etc.
    severity = db.Column(db.String(20), nullable=False)  # high, medium, low
    status = db.Column(db.String(20), default='active')  # active, resolved, false_positive
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    blocked = db.Column(db.Boolean, default=False)
    source_ip = db.Column(db.String(50))
    target_path = db.Column(db.String(255))

    # Relationships
    scan = db.relationship('Scan', backref='threats')
    alerts = db.relationship('Alert', back_populates='threat', lazy=True, cascade='all, delete-orphan')

    def __init__(self, scan_id, type, severity, description=None, source_ip=None, target_path=None):
        self.scan_id = scan_id
        self.type = type
        self.severity = severity
        self.description = description
        self.source_ip = source_ip
        self.target_path = target_path
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'type': self.type,
            'severity': self.severity,
            'status': self.status,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'blocked': self.blocked,
            'source_ip': self.source_ip,
            'target_path': self.target_path
        }

    def __repr__(self):
        return f'<ThreatAnalysis {self.type} - {self.severity}>'

    @staticmethod
    def get_active_threats_count():
        """Get count of active threats"""
        return ThreatAnalysis.query.filter_by(status='active').count()

    @staticmethod
    def get_active_threats():
        """Get all active threats"""
        return ThreatAnalysis.query.filter_by(status='active').all()

    @staticmethod
    def get_weekly_trend():
        """Calculate the percentage change in active threats over the last week"""
        from datetime import timedelta
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        # Current active threats
        current_active = ThreatAnalysis.query.filter_by(status='active').count()

        # Active threats from a week ago
        past_active = ThreatAnalysis.query.filter(
            ThreatAnalysis.timestamp <= week_ago,
            ThreatAnalysis.status == 'active'
        ).count()

        if past_active == 0:
            return 0 if current_active == 0 else 100

        change = ((current_active - past_active) / past_active) * 100
        return round(change, 1)
