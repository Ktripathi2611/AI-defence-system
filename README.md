# AI Cyber Defense System

A comprehensive cybersecurity platform that provides real-time threat detection, spam filtering, deepfake detection, and community-driven security awareness.

## Features

### 1. Real-Time Threat Detection
- URL safety scanning using multiple APIs
- IP reputation checking
- Phishing detection
- Malware identification
- Live threat monitoring dashboard

### 2. Spam Detection
- Real-time message analysis
- Email content filtering
- Chat protection
- Multiple API integration for accuracy

### 3. Deepfake Detection
- Image and video analysis
- Real-time media scanning
- High confidence scoring
- Detailed detection reports

### 4. Community Features
- User reporting system
- Threat awareness sharing
- Community-driven alerts
- Collaborative security

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- WebSocket for real-time updates
- SQLite database
- Async API integration

### Frontend
- React.js
- Material-UI components
- Real-time WebSocket connection
- Interactive dashboards

## API Integrations

The system integrates with multiple security APIs for comprehensive threat detection:

### Required APIs and Setup Instructions

1. **VirusTotal API**
   - Sign up at: https://www.virustotal.com/gui/join-us
   - Free tier: 500 requests/day
   - Used for: URL and file scanning

2. **Google Safe Browsing API**
   - Get key at: https://developers.google.com/safe-browsing
   - Free tier: 10,000 requests/day
   - Used for: Malicious URL detection

3. **DeepAI API**
   - Sign up at: https://deepai.org/
   - Free tier: 5,000 API calls/month
   - Used for: Deepfake detection

4. **AbuseIPDB**
   - Register at: https://www.abuseipdb.com/pricing
   - Free tier: 1,000 queries/day
   - Used for: IP reputation checking

5. **PhishTank API**
   - Apply at: https://www.phishtank.com/developer_info.php
   - Free tier: Unlimited requests (rate limited)
   - Used for: Phishing detection

6. **Cloudmersive API**
   - Sign up at: https://cloudmersive.com/pricing
   - Free tier: 800 API calls/month
   - Used for: Content analysis

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd ai-defense-system
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **API Configuration**
   Create a `.env` file in the backend directory:
   ```env
   VIRUSTOTAL_API_KEY=your_key
   GOOGLE_SAFE_BROWSING_KEY=your_key
   DEEPAI_API_KEY=your_key
   ABUSEIPDB_API_KEY=your_key
   PHISHTANK_API_KEY=your_key
   CLOUDMERSIVE_API_KEY=your_key
   ```

5. **Start the Application**
   
   Backend:
   ```bash
   cd backend
   python main.py
   ```

   Frontend:
   ```bash
   cd frontend
   npm start
   ```

   Access the application at: http://localhost:3000

## Real-Time Monitoring

The system provides real-time monitoring through WebSocket connections:

1. **Dashboard Statistics**
   - Spam detected count
   - Threats blocked
   - Deepfakes identified
   - Community reports

2. **Live Alerts**
   - Instant threat notifications
   - Detailed alert information
   - Severity levels
   - Timestamp tracking

## Security Considerations

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables
   - Implement key rotation

2. **Rate Limiting**
   - Monitor API usage
   - Implement request throttling
   - Cache responses when possible

3. **Data Privacy**
   - Secure data transmission
   - Limited data retention
   - User privacy protection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.
