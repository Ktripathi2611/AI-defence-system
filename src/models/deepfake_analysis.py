from datetime import datetime
from src.models import db

class DeepFakeAnalysis(db.Model):
    __tablename__ = 'deepfake_analysis'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=False)
    media_path = db.Column(db.String(500), nullable=False)
    confidence_score = db.Column(db.Float)
    is_deepfake = db.Column(db.Boolean)
    analysis_details = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    scan = db.relationship('Scan', back_populates='deepfake_analysis', single_parent=True)
    
    def __init__(self, scan_id, media_path, confidence_score=None, is_deepfake=None, analysis_details=None):
        self.scan_id = scan_id
        self.media_path = media_path
        self.confidence_score = confidence_score
        self.is_deepfake = is_deepfake
        self.analysis_details = analysis_details
        self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'media_path': self.media_path,
            'confidence_score': self.confidence_score,
            'is_deepfake': self.is_deepfake,
            'analysis_details': self.analysis_details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
        
    def __repr__(self):
        return f'<DeepFakeAnalysis {self.media_path} - {self.confidence_score}>'
