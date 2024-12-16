from src import create_app, db
from src.models.threat_analysis import ThreatAnalysis
from datetime import datetime

app = create_app()

with app.app_context():
    # Create a test threat
    test_threat = ThreatAnalysis(
        type='malware',
        severity='high',
        description='Test malware threat',
        source_ip='192.168.1.100',
        target_path='/var/www/test',
        status='active'
    )
    
    db.session.add(test_threat)
    db.session.commit()
    
    # Verify the threat was created
    active_threats = ThreatAnalysis.get_active_threats_count()
    print(f"Active threats count: {active_threats}")
    
    # Get the weekly trend
    trend = ThreatAnalysis.get_weekly_trend()
    print(f"Weekly trend: {trend}%")
