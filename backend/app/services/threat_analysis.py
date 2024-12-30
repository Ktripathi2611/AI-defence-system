from typing import Dict, List, Optional
import re
from urllib.parse import urlparse
from backend.app.core.config import settings

class ThreatAnalysisService:
    def __init__(self):
        # Initialize threat detection patterns
        self.suspicious_url_patterns = [
            r'bit\.ly',
            r'goo\.gl',
            r'tinyurl\.com',
            r'(?:http|https)://[^\s/$.?#].[^\s]*\.(exe|bat|cmd|sh|php|zip)$',
            r'(?:http|https)://\d+\.\d+\.\d+\.\d+',
            r'(?:http|https)://[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}/~'
        ]
        
        self.suspicious_file_extensions = {
            '.exe', '.bat', '.cmd', '.sh', '.vbs', '.ps1',
            '.jar', '.js', '.php', '.dll', '.scr'
        }
        
        self.stats = {
            'urls_analyzed': 0,
            'files_analyzed': 0,
            'threats_detected': 0
        }
    
    async def analyze_url(self, url: str, metadata: dict = {}) -> Dict:
        """
        Analyze a URL for potential threats
        """
        try:
            self.stats['urls_analyzed'] += 1
            parsed_url = urlparse(url)
            
            # Check for suspicious patterns
            threat_indicators = []
            for pattern in self.suspicious_url_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    threat_indicators.append(f"Matches suspicious pattern: {pattern}")
            
            # Check domain age (simplified)
            if metadata.get('domain_age_days', 30) < 30:
                threat_indicators.append("Recently registered domain")
            
            # Calculate threat score
            threat_score = len(threat_indicators) / len(self.suspicious_url_patterns)
            is_malicious = threat_score > 0.3
            
            if is_malicious:
                self.stats['threats_detected'] += 1
            
            return {
                "is_malicious": is_malicious,
                "threat_type": "suspicious_url" if is_malicious else None,
                "confidence": threat_score,
                "details": {
                    "threat_indicators": threat_indicators,
                    "domain": parsed_url.netloc,
                    "path": parsed_url.path
                },
                "safety_recommendations": [
                    "Verify the website's legitimacy before proceeding",
                    "Check for HTTPS and valid certificates",
                    "Be cautious of shortened URLs"
                ]
            }
        except Exception as e:
            raise Exception(f"Error in URL analysis: {str(e)}")

    async def analyze_file(self, file_content: bytes, file_name: str, metadata: dict = {}) -> Dict:
        """
        Analyze a file for potential threats
        """
        try:
            self.stats['files_analyzed'] += 1
            file_ext = file_name[file_name.rfind('.'):].lower() if '.' in file_name else ''
            
            # Check for suspicious patterns
            threat_indicators = []
            
            # Check file extension
            if file_ext in self.suspicious_file_extensions:
                threat_indicators.append(f"Suspicious file extension: {file_ext}")
            
            # Check file size
            file_size = len(file_content)
            if file_size < 100:  # Suspiciously small
                threat_indicators.append("Suspiciously small file size")
            elif file_size > 10 * 1024 * 1024:  # Larger than 10MB
                threat_indicators.append("Large file size")
            
            # Calculate threat score
            threat_score = len(threat_indicators) / 3  # Normalize by number of checks
            is_malicious = threat_score > 0.3
            
            if is_malicious:
                self.stats['threats_detected'] += 1
            
            return {
                "is_malicious": is_malicious,
                "threat_type": "suspicious_file" if is_malicious else None,
                "confidence": threat_score,
                "details": {
                    "threat_indicators": threat_indicators,
                    "file_name": file_name,
                    "file_size": file_size
                },
                "safety_recommendations": [
                    "Scan files with antivirus software before opening",
                    "Be cautious of executable files",
                    "Verify the file source"
                ]
            }
        except Exception as e:
            raise Exception(f"Error in file analysis: {str(e)}")

    async def get_stats(self) -> Dict[str, int]:
        """
        Get threat analysis statistics
        """
        return self.stats

# Create a singleton instance
threat_analysis_service = ThreatAnalysisService()
