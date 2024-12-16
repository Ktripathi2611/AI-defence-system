from datetime import datetime
from src.models import db

class Scan(db.Model):
    __tablename__ = 'scan'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255))
    target_url = db.Column(db.String(500))
    scan_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    completion_time = db.Column(db.DateTime)
    threats_found = db.Column(db.Integer, default=0)
    
    # Relationships
    user = db.relationship('User', back_populates='scans')
    deepfake_analysis = db.relationship('DeepFakeAnalysis', back_populates='scan', uselist=False, cascade='all, delete-orphan')

    def __init__(self, user_id, scan_type, status='pending', filename=None, target_url=None):
        self.user_id = user_id
        self.scan_type = scan_type
        self.status = status
        self.filename = filename
        self.target_url = target_url
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'target_url': self.target_url,
            'scan_type': self.scan_type,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'completion_time': self.completion_time.isoformat() if self.completion_time else None,
            'threats_found': self.threats_found,
            'error_message': self.error_message
        }
