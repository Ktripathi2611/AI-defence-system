import os
import joblib
from sklearn.ensemble import RandomForestClassifier
import re
from urllib.parse import urlparse

class URLAnalyzer:
    def __init__(self):
        self.feature_names = [
            'url_length', 'num_digits', 'num_special_chars',
            'has_ip', 'has_at', 'has_multiple_subdomains',
            'domain_length', 'path_length', 'num_params',
            'has_https', 'is_shortened'
        ]
        
        self.shortening_services = [
            'bit.ly', 'tinyurl.com', 't.co', 'goo.gl',
            'is.gd', 'cli.gs', 'ow.ly', 'buff.ly'
        ]

    def analyze(self, url: str) -> dict:
        # Demo implementation - detect common phishing patterns
        is_malicious = False
        risk_factors = []
        
        # Check for IP address in URL
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            is_malicious = True
            risk_factors.append("Contains IP address")
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.xyz', '.tk', '.pw', '.cc', '.fun', '.top']
        if any(url.lower().endswith(tld) for tld in suspicious_tlds):
            is_malicious = True
            risk_factors.append("Suspicious domain extension")
        
        # Check for suspicious keywords
        suspicious_keywords = ['login', 'signin', 'verify', 'bank', 'account', 'secure']
        if any(keyword in url.lower() for keyword in suspicious_keywords):
            is_malicious = True
            risk_factors.append("Contains suspicious keywords")
        
        # Check for excessive subdomains
        parsed_url = urlparse(url)
        subdomain_count = len(parsed_url.netloc.split('.')) - 2
        if subdomain_count > 3:
            is_malicious = True
            risk_factors.append("Excessive subdomains")

        return {
            "url": url,
            "is_malicious": is_malicious,
            "risk_factors": risk_factors,
            "risk_score": len(risk_factors) * 25 if risk_factors else 0,
            "recommendation": "Block" if is_malicious else "Allow"
        }

class PhishingDetector:
    def __init__(self):
        self.url_analyzer = URLAnalyzer()
        
    def analyze_webpage(self, url, html_content):
        # Combine URL analysis with webpage content analysis
        url_threat = self.url_analyzer.analyze(url)
        
        # Analyze HTML content for phishing indicators
        content_threat = self._analyze_content(html_content)
        
        # Combine scores
        final_score = (url_threat['risk_score'] + content_threat['threat_score']) / 2
        
        return {
            'threat_score': final_score,
            'is_phishing': final_score > 0.7,
            'confidence': min(final_score * 1.2, 1.0),
            'indicators': {
                'url_suspicious': url_threat['is_malicious'],
                'content_suspicious': content_threat['is_suspicious'],
                'security_indicators': content_threat['security_indicators']
            }
        }
    
    def _analyze_content(self, html_content):
        # Placeholder for HTML content analysis
        return {
            'threat_score': 0.5,
            'is_suspicious': False,
            'security_indicators': ['legitimate_ssl', 'no_suspicious_scripts']
        }
