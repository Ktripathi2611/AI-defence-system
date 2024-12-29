from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import numpy as np
from datetime import datetime
import json
import aiofiles
import os
import cv2
from PIL import Image
import io
from models.threat_detector import DeepFakeDetector
from models.url_analyzer import URLAnalyzer

app = FastAPI(title="AI Defense System API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specifically allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
deepfake_detector = DeepFakeDetector()
url_analyzer = URLAnalyzer()

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ThreatReport(BaseModel):
    url: str
    type: str
    description: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "AI Defense System API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "timestamp": datetime.now().isoformat()}
    )

@app.post("/analyze/url")
async def analyze_url(url: str):
    try:
        analyzer = URLAnalyzer()
        result = analyzer.analyze(url)
        
        # Record the scan in history
        SCAN_HISTORY.append({
            "type": "URL Analysis",
            "target": url,
            "status": "blocked" if result["is_malicious"] else "safe",
            "details": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/media")
async def analyze_media(file: UploadFile = File(...)):
    try:
        detector = DeepFakeDetector()
        contents = await file.read()
        
        # Convert to numpy array for image processing
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            result = detector.analyze_image(image)
        else:
            # Save video temporarily for processing
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as f:
                f.write(contents)
            
            result = detector.analyze_video(temp_path)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        # Record the scan in history
        SCAN_HISTORY.append({
            "type": "Media Analysis",
            "target": file.filename,
            "status": "blocked" if result.get("is_fake", False) else "safe",
            "details": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/report/threat")
async def report_threat(report: ThreatReport):
    try:
        # Store the report (you would typically save this to a database)
        report_id = f"THR{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Analyze the reported URL
        url_analysis = await analyze_url(report.url)
        
        return {
            "status": "received",
            "report_id": report_id,
            "url_analysis": url_analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard statistics endpoint
@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Update threats
        threat_simulator.update_threats()
        
        # Calculate stats
        blocked_count = len(threat_database["blocked_threats"])
        active_count = len(threat_database["active_threats"])
        
        # Calculate protection score (higher when fewer active threats)
        max_active_threats = 10
        protection_score = max(0, min(100, 100 - (active_count / max_active_threats * 100)))
        
        # Get system status
        system_status = [
            {
                "title": "DeepFake Detection",
                "description": "Actively monitoring for AI-generated content",
                "timestamp": datetime.now().isoformat(),
                "status": "operational"
            },
            {
                "title": "URL Analysis",
                "description": "Scanning for malicious links and phishing attempts",
                "timestamp": datetime.now().isoformat(),
                "status": "operational"
            },
            {
                "title": "Threat Database",
                "description": "Updated with latest cyber threat intelligence",
                "timestamp": datetime.now().isoformat(),
                "status": "operational"
            }
        ]
        
        return {
            "threats_blocked": blocked_count,
            "active_threats": active_count,
            "protection_score": int(protection_score),
            "recent_threats": threat_database["recent_threats"],
            "system_status": system_status,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching dashboard statistics: {str(e)}"
        )

# Endpoint to simulate a new threat (for testing)
@app.post("/simulate/threat")
async def simulate_threat():
    new_threat = threat_simulator.generate_threat()
    if new_threat["status"] == "Blocked":
        threat_database["blocked_threats"].append(new_threat)
    elif new_threat["status"] == "Active":
        threat_database["active_threats"].append(new_threat)
    threat_database["recent_threats"].insert(0, new_threat)
    threat_database["recent_threats"] = threat_database["recent_threats"][:10]
    return {"message": "New threat simulated", "threat": new_threat}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# In-memory storage for demo purposes
threat_database = {
    "blocked_threats": [],
    "active_threats": [],
    "recent_threats": []
}

class ThreatSimulator:
    def __init__(self):
        self.threat_types = [
            "Phishing Attempt",
            "Malicious URL",
            "DeepFake Content",
            "Social Engineering Attack",
            "Data Theft Attempt"
        ]
        self.last_update = datetime.now()
        self.update_interval = timedelta(minutes=5)

    def generate_threat(self) -> Dict:
        return {
            "type": random.choice(self.threat_types),
            "severity": random.choice(["Low", "Medium", "High"]),
            "timestamp": datetime.now().isoformat(),
            "description": f"Detected suspicious activity from {random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "status": random.choice(["Blocked", "Active", "Investigating"])
        }

    def update_threats(self):
        current_time = datetime.now()
        if current_time - self.last_update >= self.update_interval:
            # Simulate new threats
            if random.random() < 0.3:  # 30% chance of new threat
                new_threat = self.generate_threat()
                if new_threat["status"] == "Blocked":
                    threat_database["blocked_threats"].append(new_threat)
                elif new_threat["status"] == "Active":
                    threat_database["active_threats"].append(new_threat)
                threat_database["recent_threats"].insert(0, new_threat)
                
                # Keep only last 10 recent threats
                threat_database["recent_threats"] = threat_database["recent_threats"][:10]
            
            self.last_update = current_time

# Initialize threat simulator
threat_simulator = ThreatSimulator()

# Initialize in-memory storage for demo
SCAN_HISTORY = []

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
