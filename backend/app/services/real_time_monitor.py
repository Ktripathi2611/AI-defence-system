import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
import logging
from fastapi import WebSocket
from .api_service import APIService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeMonitor:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.stats = {
            "spam_detected": 0,
            "threats_blocked": 0,
            "deepfakes_identified": 0,
            "community_reports": 0
        }
        self.is_monitoring = False
        self.monitoring_task = None
        self.api_service = None

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
            except Exception as e:
                logger.error(f"Error broadcasting stats: {e}")
                self.active_connections.remove(connection)

    async def start_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.api_service = APIService()
            await self.api_service.__aenter__()
            self.monitoring_task = asyncio.create_task(self.monitor_threats())
            logger.info("Real-time monitoring started")

    async def stop_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitoring_task:
                self.monitoring_task.cancel()
            if self.api_service:
                await self.api_service.__aexit__(None, None, None)
            logger.info("Real-time monitoring stopped")

    async def monitor_threats(self):
        try:
            while self.is_monitoring:
                # Sample URLs and content to check
                urls_to_check = [
                    "http://example.com",
                    "https://test.com/suspicious",
                    "http://malware-test.com"
                ]
                spam_content = [
                    "Buy now! Limited offer!",
                    "You've won a prize!",
                    "Hello, this is a legitimate message"
                ]
                images_to_check = [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ]

                # Check URLs for threats
                for url in urls_to_check:
                    threat_results = await self.api_service.check_url_safety(url)
                    phishing_results = await self.api_service.check_phishing(url)
                    
                    threat_score = self.api_service.aggregate_threat_score({
                        **threat_results,
                        **phishing_results
                    })
                    
                    if threat_score > 0.7:
                        self.stats["threats_blocked"] += 1
                        await self.broadcast_alert({
                            "type": "threat",
                            "data": {
                                "url": url,
                                "threat_score": threat_score,
                                "details": "High-risk URL detected"
                            }
                        })

                # Check content for spam
                for content in spam_content:
                    spam_results = await self.api_service.analyze_spam(content)
                    spam_score = self.api_service.aggregate_spam_score(spam_results)
                    
                    if spam_score > 0.8:
                        self.stats["spam_detected"] += 1
                        await self.broadcast_alert({
                            "type": "spam",
                            "data": {
                                "content": content[:50] + "...",
                                "spam_score": spam_score,
                                "details": "Spam content detected"
                            }
                        })

                # Check images for deepfakes
                for image_url in images_to_check:
                    deepfake_results = await self.api_service.detect_deepfake(image_url)
                    if deepfake_results.get("deepai", {}).get("confidence", 0) > 0.9:
                        self.stats["deepfakes_identified"] += 1
                        await self.broadcast_alert({
                            "type": "deepfake",
                            "data": {
                                "image_url": image_url,
                                "confidence": deepfake_results["deepai"]["confidence"],
                                "details": "Potential deepfake detected"
                            }
                        })

                await self.broadcast_stats()
                await asyncio.sleep(5)  # Check every 5 seconds

        except asyncio.CancelledError:
            logger.info("Monitoring task cancelled")
        except Exception as e:
            logger.error(f"Error in threat monitoring: {e}")

    async def broadcast_alert(self, alert: Dict):
        message = {
            "type": "alert",
            "timestamp": datetime.now().isoformat(),
            "data": alert
        }
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting alert: {e}")
                self.active_connections.remove(connection)
