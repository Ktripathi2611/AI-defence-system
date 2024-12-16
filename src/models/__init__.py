from flask_sqlalchemy import SQLAlchemy
from flask import current_app

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Import models in the correct order to avoid circular dependencies
from .user import User
from .scan import Scan
from .threat_analysis import ThreatAnalysis
from .deepfake_analysis import DeepFakeAnalysis
from .notification import Notification
from .activity import Activity
from .chat import Chat
from .alert import Alert
from .system_status import SystemStatus

# Make models available at package level
__all__ = [
    'db',
    'init_db',
    'User',
    'Scan',
    'ThreatAnalysis',
    'DeepFakeAnalysis',
    'Notification',
    'Activity',
    'Chat',
    'Alert',
    'SystemStatus'
]
