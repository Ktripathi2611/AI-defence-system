from typing import Dict, List, Optional
from backend.app.core.config import settings

class SpamDetectionService:
    def __init__(self):
        # Initialize spam detection rules
        self.spam_keywords = [
            'buy now', 'free offer', 'limited time', 'click here', 
            'winner', 'lottery', 'prize', 'urgent', 'money back',
            'congratulations', 'you\'ve won', 'act fast', 'don\'t miss',
            'credit card', 'bank account', 'wire transfer'
        ]
        
        self.risk_indicators = {
            'urgency': ['urgent', 'immediate', 'act now', 'limited time'],
            'financial': ['money', 'cash', 'bank', 'credit card'],
            'pressure': ['offer expires', 'last chance', 'don\'t miss'],
            'suspicious': ['winner', 'congratulations', 'you\'ve won']
        }
    
    async def detect_spam(self, text: str, metadata: dict = {}) -> Dict:
        """
        Detect if the given text is spam
        """
        try:
            text_lower = text.lower()
            matches = [word for word in self.spam_keywords if word in text_lower]
            spam_score = len(matches) / len(self.spam_keywords)
            
            return {
                "is_spam": spam_score > 0.3,
                "confidence": spam_score,
                "details": {
                    "matched_keywords": matches,
                    "metadata": metadata
                }
            }
        except Exception as e:
            raise Exception(f"Error in spam detection: {str(e)}")

    async def analyze_text(self, text: str) -> Dict:
        """
        Analyze text for spam characteristics
        """
        try:
            text_lower = text.lower()
            scores = {}
            for category, keywords in self.risk_indicators.items():
                matches = [word for word in keywords if word in text_lower]
                scores[category] = len(matches) / len(keywords)
            
            risk_score = sum(scores.values()) / len(scores)
            
            return {
                "is_malicious": risk_score > 0.3,
                "risk_score": risk_score,
                "category_scores": scores,
                "safety_tips": [
                    "Be cautious of unsolicited messages",
                    "Don't click on suspicious links",
                    "Report spam to help protect others"
                ]
            }
        except Exception as e:
            raise Exception(f"Error in text analysis: {str(e)}")

    async def get_safety_tips(self) -> Dict[str, List[str]]:
        """
        Get safety tips for avoiding spam
        """
        return {
            "general": [
                "Be cautious of unsolicited messages",
                "Don't share sensitive information",
                "Use spam filters"
            ],
            "email": [
                "Check sender addresses carefully",
                "Be wary of urgent or threatening messages",
                "Don't open suspicious attachments"
            ],
            "social_media": [
                "Be careful with friend requests",
                "Report spam accounts",
                "Use privacy settings"
            ]
        }

# Create a singleton instance
spam_detection_service = SpamDetectionService()
