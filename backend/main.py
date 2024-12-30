from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path
import json
from typing import List
import asyncio
from datetime import datetime
from backend.app.api.routes import spam_detection, threat_analysis, deepfake_detection, user_awareness, community
from backend.app.core.config import settings
from backend.app.services.real_time_monitor import RealTimeMonitor

app = FastAPI(
    title="AI Cyber Defense System",
    description="A comprehensive platform for protecting users against cyber threats",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the frontend build directory
FRONTEND_BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "build"))
STATIC_DIR = os.path.join(FRONTEND_BUILD_DIR, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize real-time monitor
monitor = RealTimeMonitor()

# WebSocket endpoint for real-time monitoring
@app.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    await monitor.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            command = json.loads(data)
            if command.get("action") == "start_monitoring":
                monitor.start_monitoring()
            elif command.get("action") == "stop_monitoring":
                monitor.stop_monitoring()
    except WebSocketDisconnect:
        monitor.disconnect(websocket)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stats = {
            "spam_detected": 0,
            "threats_blocked": 0,
            "deepfakes_identified": 0,
            "community_reports": 0
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.send_stats(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_stats(self, websocket: WebSocket):
        await websocket.send_json(self.stats)

    async def broadcast_stats(self):
        for connection in self.active_connections:
            try:
                await connection.send_json(self.stats)
            except WebSocketDisconnect:
                self.active_connections.remove(connection)

    def update_stats(self, stat_type: str):
        if stat_type in self.stats:
            self.stats[stat_type] += 1

manager = ConnectionManager()

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
            # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Simulate real-time updates (for testing)
async def update_stats_periodically():
    while True:
        await asyncio.sleep(5)  # Update every 5 seconds
        # Simulate random updates
        import random
        stat_types = ["spam_detected", "threats_blocked", "deepfakes_identified", "community_reports"]
        stat_type = random.choice(stat_types)
        manager.update_stats(stat_type)
        await manager.broadcast_stats()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_stats_periodically())

# Include all routers without authentication
app.include_router(
    spam_detection.router, 
    prefix="/api/spam", 
    tags=["Spam Detection"]
)
app.include_router(
    threat_analysis.router, 
    prefix="/api/threats", 
    tags=["Threat Analysis"]
)
app.include_router(
    deepfake_detection.router, 
    prefix="/api/deepfake", 
    tags=["Deepfake Detection"]
)
app.include_router(
    user_awareness.router, 
    prefix="/api/awareness", 
    tags=["User Awareness"]
)
app.include_router(
    community.router, 
    prefix="/api/community", 
    tags=["Community"]
)

# Serve index.html for all other routes
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # First check if the path exists in the build directory
    requested_path = os.path.join(FRONTEND_BUILD_DIR, full_path)
    if os.path.exists(requested_path) and os.path.isfile(requested_path):
        return FileResponse(requested_path)
    
    # If not found or is a directory, serve index.html
    return FileResponse(os.path.join(FRONTEND_BUILD_DIR, "index.html"))

@app.get("/")
async def serve_spa(path: str = ""):
    return FileResponse("frontend/build/index.html")

@app.get("/api")
async def root():
    return {
        "message": "Welcome to AI Cyber Defense System API",
        "docs_url": "/docs",
        "version": settings.VERSION
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "features": {
            "spam_detection": settings.ENABLE_SPAM_DETECTION,
            "deepfake_detection": settings.ENABLE_DEEPFAKE_DETECTION,
            "threat_analysis": settings.ENABLE_THREAT_ANALYSIS,
            "community_reporting": settings.ENABLE_COMMUNITY_REPORTING
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
