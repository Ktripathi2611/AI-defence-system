from datetime import datetime
from src.models import db

class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', back_populates='notifications')
    
    def __init__(self, user_id, type, data=None):
        self.user_id = user_id
        self.type = type
        self.data = data
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'data': self.data,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }
        
    def mark_as_read(self):
        self.read = True
        db.session.commit()
        
    def __repr__(self):
        return f'<Notification {self.id} - {self.type}>'
