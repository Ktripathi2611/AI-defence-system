from datetime import datetime
from . import db

class SystemStatus(db.Model):
    """Model for tracking system status."""
    __tablename__ = 'system_status'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False, default='stopped')  # running, stopped
    last_state_change = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemStatus {self.status}>'
