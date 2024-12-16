from datetime import datetime
from .. import db

class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    email_threats = db.Column(db.Boolean, default=True)
    email_alerts = db.Column(db.Boolean, default=True)
    desktop_notifications = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Notifications {self.id}>'

    @staticmethod
    def get_system_notifications():
        """Get system-wide notification settings"""
        notifications = Notifications.query.first()
        if not notifications:
            notifications = Notifications()
            db.session.add(notifications)
            db.session.commit()
        return notifications
