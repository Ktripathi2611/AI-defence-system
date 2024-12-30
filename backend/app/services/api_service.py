import aiohttp
import asyncio
from typing import Dict, Any, List
from ..core.config import get_settings
import logging
from datetime import datetime

settings = get_settings()
logger = logging.getLogger(__name__)

class APIService:
    def __init__(self):
        self.settings = settings
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_url_safety(self, url: str) -> Dict[str, Any]:
        """Check URL safety using multiple APIs"""
        results = {}
        
        # VirusTotal
        if self.settings.VIRUSTOTAL_API_KEY:
            try:
                async with self.session.post(
                    f"{self.settings.VIRUSTOTAL_URL}/url/report",
                    params={
                        "apikey": self.settings.VIRUSTOTAL_API_KEY,
                        "resource": url
                    }
                ) as response:
                    results["virustotal"] = await response.json()
            except Exception as e:
                logger.error(f"VirusTotal API error: {e}")

        # Google Safe Browsing
        if self.settings.GOOGLE_SAFE_BROWSING_KEY:
            try:
                payload = {
                    "client": {
                        "clientId": "ai-cyber-defense",
                        "clientVersion": "1.0.0"
                    },
                    "threatInfo": {
                        "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
                        "platformTypes": ["ANY_PLATFORM"],
                        "threatEntryTypes": ["URL"],
                        "threatEntries": [{"url": url}]
                    }
                }
                async with self.session.post(
                    f"{self.settings.SAFE_BROWSING_URL}/threatMatches:find",
                    params={"key": self.settings.GOOGLE_SAFE_BROWSING_KEY},
                    json=payload
                ) as response:
                    results["safe_browsing"] = await response.json()
            except Exception as e:
                logger.error(f"Safe Browsing API error: {e}")

        return results

    async def analyze_spam(self, content: str) -> Dict[str, Any]:
        """Analyze content for spam using multiple APIs"""
        results = {}
        
        # SpamAssassin
        if self.settings.SPAM_ASSASSIN_API_KEY:
            try:
                async with self.session.post(
                    f"{self.settings.SPAM_ASSASSIN_URL}/check",
                    headers={"X-API-Key": self.settings.SPAM_ASSASSIN_API_KEY},
                    json={"text": content}
                ) as response:
                    results["spamassassin"] = await response.json()
            except Exception as e:
                logger.error(f"SpamAssassin API error: {e}")

        # Cloudmersive
        if self.settings.CLOUDMERSIVE_API_KEY:
            try:
                async with self.session.post(
                    f"{self.settings.CLOUDMERSIVE_URL}/nlp/analytics/profanity",
                    headers={"Apikey": self.settings.CLOUDMERSIVE_API_KEY},
                    json={"textToParse": content}
                ) as response:
                    results["cloudmersive"] = await response.json()
            except Exception as e:
                logger.error(f"Cloudmersive API error: {e}")

        return results

    async def detect_deepfake(self, image_url: str) -> Dict[str, Any]:
        """Detect deepfakes using DeepAI API"""
        results = {}
        
        if self.settings.DEEPAI_API_KEY:
            try:
                async with self.session.post(
                    f"{self.settings.DEEPAI_URL}/deepfake-detection",
                    headers={"api-key": self.settings.DEEPAI_API_KEY},
                    data={"image": image_url}
                ) as response:
                    results["deepai"] = await response.json()
            except Exception as e:
                logger.error(f"DeepAI API error: {e}")

        return results

    async def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation using AbuseIPDB"""
        results = {}
        
        if self.settings.ABUSEIPDB_API_KEY:
            try:
                async with self.session.get(
                    f"{self.settings.ABUSEIPDB_URL}/check",
                    headers={"Key": self.settings.ABUSEIPDB_API_KEY},
                    params={"ipAddress": ip, "maxAgeInDays": 90}
                ) as response:
                    results["abuseipdb"] = await response.json()
            except Exception as e:
                logger.error(f"AbuseIPDB API error: {e}")

        return results

    async def check_phishing(self, url: str) -> Dict[str, Any]:
        """Check for phishing using PhishTank API"""
        results = {}
        
        if self.settings.PHISHTANK_API_KEY:
            try:
                async with self.session.post(
                    f"{self.settings.PHISHTANK_URL}/checkurl",
                    headers={"Api-Key": self.settings.PHISHTANK_API_KEY},
                    data={"url": url, "format": "json"}
                ) as response:
                    results["phishtank"] = await response.json()
            except Exception as e:
                logger.error(f"PhishTank API error: {e}")

        return results

    @staticmethod
    def aggregate_threat_score(api_results: Dict[str, Any]) -> float:
        """Aggregate threat scores from multiple APIs"""
        score = 0
        weight = 0
        
        if "virustotal" in api_results:
            score += api_results["virustotal"].get("positives", 0) * 0.4
            weight += 0.4
            
        if "safe_browsing" in api_results:
            matches = len(api_results["safe_browsing"].get("matches", []))
            score += (1 if matches > 0 else 0) * 0.3
            weight += 0.3
            
        if "phishtank" in api_results:
            score += (1 if api_results["phishtank"].get("in_database", False) else 0) * 0.3
            weight += 0.3
            
        return score / weight if weight > 0 else 0

    @staticmethod
    def aggregate_spam_score(api_results: Dict[str, Any]) -> float:
        """Aggregate spam scores from multiple APIs"""
        score = 0
        weight = 0
        
        if "spamassassin" in api_results:
            score += api_results["spamassassin"].get("score", 0) * 0.6
            weight += 0.6
            
        if "cloudmersive" in api_results:
            score += api_results["cloudmersive"].get("profanity_score", 0) * 0.4
            weight += 0.4
            
        return score / weight if weight > 0 else 0
