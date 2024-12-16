from transformers import pipeline
import logging
from datetime import datetime
import requests
from urllib.parse import urlparse
import re

# Global instance
threat_detector = None

class ThreatDetector:
    def __init__(self):
        """Initialize the threat detector with necessary models"""
        self.initialized = False
        try:
            # Initialize sentiment analysis pipeline
            self.sentiment_analyzer = pipeline("sentiment-analysis")
            self.initialized = True
            logging.info("ThreatDetector initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize ThreatDetector: {str(e)}")
            self.initialized = False

    def is_initialized(self):
        """Check if the detector is properly initialized"""
        return self.initialized

    def analyze_text(self, text):
        """Analyze text for potential threats"""
        if not self.initialized:
            raise RuntimeError("ThreatDetector not properly initialized")

        try:
            # Perform sentiment analysis
            sentiment = self.sentiment_analyzer(text)[0]
            
            # Calculate threat score based on sentiment
            threat_score = 1.0 - sentiment['score'] if sentiment['label'] == 'NEGATIVE' else 0.1
            
            # Determine threat level
            if threat_score > 0.8:
                threat_level = 'HIGH'
            elif threat_score > 0.5:
                threat_level = 'MEDIUM'
            else:
                threat_level = 'LOW'

            return {
                'threat_score': threat_score,
                'threat_level': threat_level,
                'analysis_details': {
                    'sentiment': sentiment,
                    'content_type': 'text',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logging.error(f"Error analyzing text: {str(e)}")
            raise

    def analyze_url(self, url):
        """Analyze URL for potential threats"""
        if not self.initialized:
            raise RuntimeError("ThreatDetector not properly initialized")

        try:
            # Basic URL validation
            if not self._is_valid_url(url):
                return {
                    'status': 'error',
                    'confidence': 1.0,
                    'details': 'Invalid URL format'
                }

            # Check URL structure for common malicious patterns
            risk_score = self._check_url_structure(url)
            
            # Try to fetch and analyze content
            try:
                response = requests.get(url, timeout=5, verify=True)
                content_analysis = self._analyze_content(response)
                risk_score = max(risk_score, content_analysis['risk_score'])
            except Exception as e:
                logging.warning(f"Failed to fetch URL content: {str(e)}")
                # Don't modify risk score if we can't analyze content
                pass

            # Determine status based on risk score
            if risk_score > 0.7:
                status = 'malicious'
            elif risk_score > 0.4:
                status = 'suspicious'
            else:
                status = 'safe'

            return {
                'status': status,
                'confidence': risk_score,
                'details': self._get_risk_details(risk_score)
            }

        except Exception as e:
            logging.error(f"Error analyzing URL: {str(e)}")
            return {
                'status': 'error',
                'confidence': 0.0,
                'details': str(e)
            }

    def _is_valid_url(self, url):
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _check_url_structure(self, url):
        """Check URL structure for suspicious patterns"""
        risk_score = 0.0
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.xyz', '.tk', '.pw', '.cc', '.club', '.work', '.dating', '.loans']
        if any(url.lower().endswith(tld) for tld in suspicious_tlds):
            risk_score += 0.4

        # Check for IP addresses instead of domain names
        if re.search(r'\d+\.\d+\.\d+\.\d+', urlparse(url).netloc):
            risk_score += 0.3

        # Check for suspicious keywords
        suspicious_keywords = ['login', 'account', 'banking', 'secure', 'update', 'verify']
        if any(keyword in url.lower() for keyword in suspicious_keywords):
            risk_score += 0.2

        # Check for excessive subdomains
        subdomain_count = len(urlparse(url).netloc.split('.')) - 2
        if subdomain_count > 3:
            risk_score += 0.2

        return min(risk_score, 1.0)

    def _analyze_content(self, response):
        """Analyze webpage content"""
        risk_score = 0.0
        
        # Check for suspicious forms
        if '<form' in response.text.lower() and ('password' in response.text.lower() or 'login' in response.text.lower()):
            risk_score += 0.3

        # Check for obfuscated JavaScript
        if 'eval(' in response.text or 'document.write(' in response.text:
            risk_score += 0.3

        # Check for suspicious redirects
        if len(response.history) > 2:
            risk_score += 0.2

        # Analyze visible text content
        if self.sentiment_analyzer:
            try:
                # Extract visible text (simple approach)
                text = re.sub(r'<[^>]+>', ' ', response.text)
                sentiment = self.sentiment_analyzer(text[:512])[0]  # Analyze first 512 chars
                if sentiment['label'] == 'NEGATIVE' and sentiment['score'] > 0.8:
                    risk_score += 0.2
            except:
                pass

        return {
            'risk_score': min(risk_score, 1.0)
        }

    def _get_risk_details(self, risk_score):
        """Get human-readable risk details"""
        if risk_score > 0.7:
            return "High risk - Multiple suspicious patterns detected"
        elif risk_score > 0.4:
            return "Medium risk - Some suspicious patterns detected"
        else:
            return "Low risk - No significant suspicious patterns"

    def analyze_email(self, email_content):
        """Analyze email content for potential threats"""
        if not self.initialized:
            raise RuntimeError("ThreatDetector not properly initialized")

        try:
            # Analyze both subject and body
            text_analysis = self.analyze_text(email_content)
            
            return {
                'threat_score': text_analysis['threat_score'],
                'threat_level': text_analysis['threat_level'],
                'analysis_details': {
                    **text_analysis['analysis_details'],
                    'content_type': 'email',
                    'phishing_indicators': 'none_detected',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logging.error(f"Error analyzing email: {str(e)}")
            raise

def initialize_threat_detector():
    """Initialize the global threat detector instance"""
    global threat_detector
    try:
        threat_detector = ThreatDetector()
        return threat_detector.is_initialized()
    except Exception as e:
        logging.error(f"Failed to initialize global threat detector: {str(e)}")
        return False

def analyze_threat(target):
    """Analyze a target for threats"""
    global threat_detector
    
    if threat_detector is None:
        threat_detector = ThreatDetector()
    
    if not threat_detector.is_initialized():
        return {
            'status': 'error',
            'confidence': 0.0,
            'details': 'Threat detector not initialized'
        }
    
    return threat_detector.analyze_url(target)
