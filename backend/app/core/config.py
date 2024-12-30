from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Base Configuration
    PROJECT_NAME: str = "AI Cyber Defense System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security and Authentication
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # External APIs
    VIRUSTOTAL_API_KEY: Optional[str] = None
    SPAM_ASSASSIN_API_KEY: Optional[str] = None
    DEEPAI_API_KEY: Optional[str] = None
    ABUSEIPDB_API_KEY: Optional[str] = None
    PHISHTANK_API_KEY: Optional[str] = None
    GOOGLE_SAFE_BROWSING_KEY: Optional[str] = None
    CLOUDMERSIVE_API_KEY: Optional[str] = None
    
    # Service URLs
    VIRUSTOTAL_URL: str = "https://www.virustotal.com/vtapi/v2"
    SPAM_ASSASSIN_URL: str = "https://api.spamassassin.org"
    DEEPAI_URL: str = "https://api.deepai.org/api"
    ABUSEIPDB_URL: str = "https://api.abuseipdb.com/api/v2"
    PHISHTANK_URL: str = "https://api.phishtank.com"
    SAFE_BROWSING_URL: str = "https://safebrowsing.googleapis.com/v4"
    CLOUDMERSIVE_URL: str = "https://api.cloudmersive.com"
    
    # Database
    DATABASE_URL: str = "sqlite:///./cyber_defense.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
