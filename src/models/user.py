from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from src.models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')
    
    # Relationships
    scans = db.relationship('Scan', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', lazy=True, cascade='all, delete-orphan')
    alerts_resolved = db.relationship('Alert', 
                                    foreign_keys='Alert.resolved_by', 
                                    backref=db.backref('resolved_by_user', lazy=True))
    threats_resolved = db.relationship('ThreatAnalysis', 
                                     foreign_keys='ThreatAnalysis.resolved_by',
                                     backref=db.backref('resolved_by_user', lazy=True))

    def __init__(self, username, email, role='user'):
        self.username = username
        self.email = email
        self.role = role
        self.created_at = datetime.utcnow()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'
