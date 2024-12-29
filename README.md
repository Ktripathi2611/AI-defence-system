# AI Cyber Defense Platform

A comprehensive AI-powered platform designed to combat cyber-crimes and enhance user safety. The platform includes a backend API, frontend web application, and Chrome extension for real-time threat detection.

## 🌟 Features

- **URL Analysis**: Real-time detection of phishing and malicious URLs
- **Deepfake Detection**: AI-powered analysis of images and videos
- **Threat Reporting**: User-driven threat reporting system
- **Chrome Extension**: Real-time website safety monitoring
- **Dashboard**: Comprehensive threat monitoring and statistics

## 🏗️ Architecture

The platform consists of three main components:

### 1. Backend (FastAPI)

Located in `/backend/`:

- **main.py**: Core API server with endpoints for URL analysis, media processing, and threat reporting
- **models/**
  - **url_analyzer.py**: ML-based URL analysis with feature extraction
  - **threat_detector.py**: Deepfake detection using EfficientNetB0
  
Key Features:
- Asynchronous request handling
- ML model integration
- File upload processing
- CORS support
- Error handling and logging

### 2. Frontend (React)

Located in `/frontend/`:

- **Components/**
  - **DeepFakeDetector**: Media upload and analysis interface
  - **ThreatAwareness**: Educational content about cyber threats
  - **ReportThreat**: Threat reporting interface
  - **Navbar**: Navigation component
- **Pages/**
  - Dashboard, Analysis, Reports pages
- **Services/**
  - API integration
  - State management

### 3. Chrome Extension

Located in `/chrome-extension/`:

- **popup.html/js**: Extension UI and core functionality
- **background.js**: Background processes and threat monitoring
- **manifest.json**: Extension configuration
- **styles.css**: UI styling

Features:
- Real-time URL analysis
- Threat statistics
- Recent threats history
- One-click reporting

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Docker (optional)

### Installation

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Chrome Extension Setup**
   - Open Chrome
   - Go to `chrome://extensions/`
   - Enable Developer Mode
   - Click "Load unpacked"
   - Select the `/chrome-extension` directory

### Running the Application

1. **Start Backend**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start Frontend**
   ```bash
   cd frontend
   npm start
   ```

3. **Docker Deployment**
   ```bash
   docker-compose up --build
   ```

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/db
JWT_SECRET=your-secret-key
MODEL_PATH=path/to/models

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

## 🛡️ Security Features

1. **URL Analysis**
   - Domain reputation checking
   - Phishing pattern detection
   - SSL/TLS verification
   - URL structure analysis

2. **Deepfake Detection**
   - EfficientNetB0-based image analysis
   - Video frame analysis
   - Artifact detection
   - Confidence scoring

3. **General Security**
   - CORS protection
   - Rate limiting
   - Input validation
   - Error handling

## 📊 API Endpoints

### URL Analysis
- `POST /analyze/url`
  - Analyzes URLs for potential threats
  - Returns threat level and details

### Media Analysis
- `POST /analyze/media`
  - Processes images/videos for deepfake detection
  - Supports multiple file formats

### Threat Reporting
- `POST /report/threat`
  - Allows users to report suspicious content
  - Stores reports for analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔍 Future Enhancements

- [ ] Advanced ML model training
- [ ] Real-time video analysis
- [ ] Browser extension for Firefox
- [ ] Mobile application
- [ ] API documentation with Swagger
- [ ] Enhanced threat intelligence integration
