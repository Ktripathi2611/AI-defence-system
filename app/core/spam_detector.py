from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from typing import Dict, Any
import re

class SpamDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.classifier = MultinomialNB()
        self.spam_patterns = self._load_spam_patterns()
        
    def _load_spam_patterns(self):
        return {
            'promotional': [
                r'limited.*offer',
                r'act.*now',
                r'exclusive.*deal',
                r'congratulations.*won'
            ],
            'scam': [
                r'bank.*account.*verify',
                r'inheritance.*claim',
                r'lottery.*winner',
                r'investment.*opportunity'
            ],
            'phishing': [
                r'password.*expired',
                r'account.*suspended',
                r'security.*alert',
                r'unusual.*activity'
            ]
        }
        
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze text content for spam characteristics.
        Returns analysis results including spam probability and detected patterns.
        """
        result = {
            'is_spam': False,
            'spam_probability': 0.0,
            'detected_patterns': [],
            'spam_type': None,
            'confidence': 0.0
        }
        
        # Check for spam patterns
        for spam_type, patterns in self.spam_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    result['detected_patterns'].append({
                        'type': spam_type,
                        'pattern': pattern
                    })
                    
        # Calculate spam probability based on detected patterns
        pattern_count = len(result['detected_patterns'])
        if pattern_count > 0:
            result['spam_probability'] = min(0.95, pattern_count * 0.2)
            
            # Determine most likely spam type
            spam_types = [p['type'] for p in result['detected_patterns']]
            if spam_types:
                result['spam_type'] = max(set(spam_types), key=spam_types.count)
                
        # Additional text analysis
        text_features = self._extract_text_features(content)
        result['confidence'] = self._calculate_confidence(text_features)
        
        # Final spam determination
        result['is_spam'] = result['spam_probability'] > 0.5
        
        return result
        
    def _extract_text_features(self, text: str) -> Dict[str, float]:
        """Extract relevant features from text for spam analysis."""
        features = {
            'caps_ratio': self._calculate_caps_ratio(text),
            'special_chars_ratio': self._calculate_special_chars_ratio(text),
            'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
            'exclamation_count': text.count('!')
        }
        return features
        
    def _calculate_caps_ratio(self, text: str) -> float:
        """Calculate ratio of uppercase letters in text."""
        if not text:
            return 0.0
        caps_count = sum(1 for c in text if c.isupper())
        return caps_count / len(text)
        
    def _calculate_special_chars_ratio(self, text: str) -> float:
        """Calculate ratio of special characters in text."""
        if not text:
            return 0.0
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        return special_chars / len(text)
        
    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence score based on extracted features."""
        confidence = 0.0
        
        # Suspicious patterns in features
        if features['caps_ratio'] > 0.5:
            confidence += 0.2
        if features['special_chars_ratio'] > 0.1:
            confidence += 0.2
        if features['url_count'] > 2:
            confidence += 0.2
        if features['exclamation_count'] > 3:
            confidence += 0.2
            
        return min(0.95, confidence)
