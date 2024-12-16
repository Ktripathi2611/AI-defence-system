from datetime import datetime, timedelta
import random
from src import db
from src.models import User, ThreatAnalysis, Alert

def initialize_sample_data():
    # Clear existing data
    User.query.delete()
    ThreatAnalysis.query.delete()
    Alert.query.delete()
    
    # Create test user
    test_user = User(
        email='admin@example.com',
        name='Admin User',
        created_at=datetime.utcnow(),
        last_login=datetime.utcnow()
    )
    test_user.set_password('admin123')
    db.session.add(test_user)
    
    # Create sample threat data
    threat_types = ['malware', 'phishing', 'ddos', 'other']
    severities = ['high', 'medium', 'low']
    
    # Generate threats for the last 7 days
    for i in range(7):
        date = datetime.utcnow() - timedelta(days=i)
        num_threats = random.randint(5, 15)
        
        for _ in range(num_threats):
            threat = ThreatAnalysis(
                type=random.choice(threat_types),
                severity=random.choice(severities),
                description=f"Sample threat detected on {date.strftime('%Y-%m-%d')}",
                source_ip=f"192.168.1.{random.randint(1, 255)}",
                destination_ip=f"10.0.0.{random.randint(1, 255)}"
            )
            threat.timestamp = date
            db.session.add(threat)
    
    # Create sample alerts
    alert_titles = [
        "Suspicious login attempt detected",
        "Unusual network activity observed",
        "Potential data breach attempt",
        "System update required",
        "Firewall rule violation"
    ]
    
    for title in alert_titles:
        alert = Alert(
            title=title,
            severity=random.choice(severities),
            description=f"Sample alert: {title}"
        )
        db.session.add(alert)
    
    db.session.commit()

if __name__ == '__main__':
    initialize_sample_data()
