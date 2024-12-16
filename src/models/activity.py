from datetime import datetime
from .. import db

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'description': self.description,
            'timestamp': self.timestamp.isoformat()
        }
    
    @staticmethod
    def log_activity(activity_type, description):
        """Log a system activity"""
        activity = Activity(
            activity_type=activity_type,
            description=description
        )
        db.session.add(activity)
        db.session.commit()
        return activity
