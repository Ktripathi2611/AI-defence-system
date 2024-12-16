from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta
import random

# Create blueprint
main = Blueprint('main', __name__)

@main.route('/')
@main.route('/dashboard')
def dashboard():
    # Sample data for the dashboard
    total_threats = random.randint(150, 300)
    active_alerts = random.randint(5, 20)
    
    # Sample recent alerts
    severities = ['high', 'medium', 'low']
    threat_types = ['Malware Detected', 'Suspicious Activity', 'Unauthorized Access', 
                   'Port Scan', 'DDoS Attempt', 'SQL Injection']
    
    recent_alerts = []
    for _ in range(5):
        timestamp = datetime.now() - timedelta(minutes=random.randint(5, 300))
        alert = {
            'title': random.choice(threat_types),
            'severity': random.choice(severities),
            'timestamp': timestamp.strftime("%I:%M %p")
        }
        recent_alerts.append(alert)
    
    return render_template('dashboard.html',
                         total_threats=total_threats,
                         active_alerts=active_alerts,
                         recent_alerts=recent_alerts)

@main.route('/api/threat-activity')
def threat_activity():
    # Sample data for threat activity over time
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    data = [random.randint(5, 25) for _ in range(7)]
    
    return jsonify({
        'labels': days,
        'data': data
    })

@main.route('/api/threat-distribution')
def threat_distribution():
    # Sample data for threat distribution
    categories = ['Malware', 'Phishing', 'DDoS', 'Other']
    data = [35, 25, 20, 20]  # Percentages
    
    return jsonify({
        'labels': categories,
        'data': data
    })

@main.route('/scan')
def scan():
    return render_template('scan.html')

@main.route('/reports')
def reports():
    return render_template('reports.html')

@main.route('/settings')
def settings():
    return render_template('settings.html')
