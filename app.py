from flask import Flask, render_template, jsonify, request
from app.core.threat_analyzer import ThreatAnalyzer
from app.core.deepfake_detector import DeepfakeDetector
from app.core.spam_detector import SpamDetector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components
threat_analyzer = ThreatAnalyzer()
deepfake_detector = DeepfakeDetector()
spam_detector = SpamDetector()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scan-url', methods=['POST'])
def scan_url():
    url = request.json.get('url')
    result = threat_analyzer.analyze_url(url)
    return jsonify(result)

@app.route('/api/detect-deepfake', methods=['POST'])
def detect_deepfake():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    result = deepfake_detector.analyze(file)
    return jsonify(result)

@app.route('/api/check-spam', methods=['POST'])
def check_spam():
    content = request.json.get('content')
    result = spam_detector.analyze(content)
    return jsonify(result)

@app.route('/api/report-threat', methods=['POST'])
def report_threat():
    threat_data = request.json
    threat_analyzer.record_threat(threat_data)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
