from typing import Dict, List
import json
import os
from datetime import datetime
from backend.app.core.config import settings

class UserAwarenessService:
    def __init__(self):
        self.tips_cache = {}
        self.load_security_tips()

    def load_security_tips(self):
        """Load security tips from JSON file or create default ones"""
        tips_file = os.path.join(settings.MODEL_PATH, "security_tips.json")
        
        if not os.path.exists(tips_file):
            self.tips_cache = {
                "phishing": [
                    {
                        "title": "Check the Sender",
                        "description": "Verify the email address carefully. Scammers often use addresses that look similar to legitimate ones.",
                        "action_items": [
                            "Look for slight misspellings in email addresses",
                            "Hover over sender name to see actual email address",
                            "Don't trust display names alone"
                        ]
                    },
                    {
                        "title": "Verify Links",
                        "description": "Always check where links lead before clicking them.",
                        "action_items": [
                            "Hover over links to see destination URL",
                            "Look for subtle misspellings in URLs",
                            "Use our URL scanner before clicking"
                        ]
                    }
                ],
                "deepfake": [
                    {
                        "title": "Check for Visual Artifacts",
                        "description": "Look for common signs of deepfake manipulation in images and videos.",
                        "action_items": [
                            "Look for unnatural eye movements",
                            "Check for blurry or inconsistent areas",
                            "Watch for audio-visual sync issues"
                        ]
                    }
                ],
                "password": [
                    {
                        "title": "Create Strong Passwords",
                        "description": "Use complex passwords to protect your accounts.",
                        "action_items": [
                            "Use at least 12 characters",
                            "Mix letters, numbers, and symbols",
                            "Avoid personal information"
                        ]
                    }
                ],
                "general": [
                    {
                        "title": "Keep Software Updated",
                        "description": "Regular updates help protect against known vulnerabilities.",
                        "action_items": [
                            "Enable automatic updates",
                            "Update all devices regularly",
                            "Don't skip security patches"
                        ]
                    }
                ]
            }
            # Save default tips
            os.makedirs(os.path.dirname(tips_file), exist_ok=True)
            with open(tips_file, 'w') as f:
                json.dump(self.tips_cache, f, indent=2)

    async def get_security_tips(self, category: str = None) -> List[Dict]:
        """Get security tips by category"""
        if category and category in self.tips_cache:
            return self.tips_cache[category]
        return [tip for tips in self.tips_cache.values() for tip in tips]

    async def get_learning_modules(self) -> List[Dict]:
        """Get available learning modules"""
        return [
            {
                "id": "phishing-101",
                "title": "Phishing Awareness 101",
                "description": "Learn to identify and avoid phishing attempts",
                "duration": "15 minutes",
                "topics": [
                    "Common phishing tactics",
                    "Red flags in emails",
                    "Safe browsing practices"
                ]
            },
            {
                "id": "deepfake-detection",
                "title": "Spotting Deepfakes",
                "description": "Understanding and identifying manipulated media",
                "duration": "20 minutes",
                "topics": [
                    "What are deepfakes",
                    "Common indicators",
                    "Verification tools"
                ]
            },
            {
                "id": "password-security",
                "title": "Password Best Practices",
                "description": "Creating and managing secure passwords",
                "duration": "10 minutes",
                "topics": [
                    "Password creation guidelines",
                    "Password managers",
                    "Two-factor authentication"
                ]
            }
        ]

    async def get_security_quiz(self, module_id: str) -> Dict:
        """Get quiz questions for a learning module"""
        quizzes = {
            "phishing-101": {
                "questions": [
                    {
                        "id": 1,
                        "question": "What should you check first in a suspicious email?",
                        "options": [
                            "The sender's email address",
                            "The email's subject line",
                            "The email's formatting",
                            "The attachments"
                        ],
                        "correct": 0
                    },
                    {
                        "id": 2,
                        "question": "Which of these is a common sign of a phishing email?",
                        "options": [
                            "Contains your full name",
                            "Urgent request for action",
                            "Sent during business hours",
                            "Has a company logo"
                        ],
                        "correct": 1
                    }
                ]
            },
            "deepfake-detection": {
                "questions": [
                    {
                        "id": 1,
                        "question": "What is a common sign of a deepfake video?",
                        "options": [
                            "High resolution",
                            "Unnatural eye movement",
                            "Clear audio",
                            "Steady camera"
                        ],
                        "correct": 1
                    }
                ]
            }
        }
        return quizzes.get(module_id, {"questions": []})

    async def get_real_world_examples(self) -> List[Dict]:
        """Get sanitized real-world examples of cyber threats"""
        return [
            {
                "type": "phishing",
                "title": "Netflix Account Suspension Scam",
                "description": "Scammers sent emails claiming Netflix accounts were suspended, asking users to update payment information.",
                "indicators": [
                    "Urgent language",
                    "Generic greeting",
                    "Suspicious sender address",
                    "Link to fake login page"
                ],
                "prevention_tips": [
                    "Check sender's email domain",
                    "Visit Netflix directly instead of clicking links",
                    "Look for personalization in the email"
                ]
            },
            {
                "type": "deepfake",
                "title": "CEO Voice Scam",
                "description": "Criminals used AI to clone a CEO's voice and requested emergency wire transfer.",
                "indicators": [
                    "Unusual request timing",
                    "Pressure to act quickly",
                    "Slight audio irregularities",
                    "Deviation from standard procedures"
                ],
                "prevention_tips": [
                    "Verify requests through alternative channels",
                    "Follow standard authorization procedures",
                    "Be wary of urgent financial requests"
                ]
            }
        ]

    async def get_emergency_resources(self) -> Dict:
        """Get emergency resources and contact information"""
        return {
            "immediate_actions": [
                "Disconnect from the network",
                "Document everything",
                "Change critical passwords",
                "Contact IT support"
            ],
            "reporting_authorities": [
                {
                    "name": "National Cyber Crime Portal",
                    "url": "https://cybercrime.gov.in/",
                    "phone": "1930"
                },
                {
                    "name": "Local Cyber Cell",
                    "description": "Contact your local police cyber cell"
                }
            ],
            "support_resources": [
                {
                    "name": "Identity Theft Resource Center",
                    "url": "https://www.idtheftcenter.org/",
                    "phone": "888-400-5530"
                }
            ]
        }

user_awareness_service = UserAwarenessService()
