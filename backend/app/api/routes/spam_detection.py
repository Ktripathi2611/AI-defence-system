from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from pydantic import BaseModel, HttpUrl
from backend.app.services.spam_detection import spam_detection_service
from backend.app.core.security import get_current_user

router = APIRouter()

class TextAnalysisRequest(BaseModel):
    text: str

class URLAnalysisRequest(BaseModel):
    url: HttpUrl

class SpamAnalysisResponse(BaseModel):
    is_spam: bool
    spam_probability: float
    confidence: float

class URLAnalysisResponse(BaseModel):
    is_malicious: bool
    risk_score: float
    safety_tips: List[str]

class SpamDetectionRequest(BaseModel):
    text: str
    metadata: dict = {}

class SpamDetectionResponse(BaseModel):
    is_spam: bool
    confidence: float
    details: dict = {}

@router.post("/analyze/text", response_model=SpamAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text for spam content
    """
    try:
        result = spam_detection_service.detect_spam(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/url", response_model=URLAnalysisResponse)
async def analyze_url(request: URLAnalysisRequest):
    """
    Analyze URL for potential malicious content
    """
    try:
        result = spam_detection_service.analyze_url(str(request.url))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect", response_model=SpamDetectionResponse)
async def detect_spam(request: SpamDetectionRequest, current_user = Depends(get_current_user)):
    try:
        result = await spam_detection_service.detect_spam(request.text, request.metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tips", response_model=Dict[str, List[str]])
async def get_safety_tips():
    """
    Get general safety tips for avoiding spam and phishing
    """
    return {
        "tips": [
            "Never share sensitive information through email",
            "Be cautious of unexpected attachments",
            "Verify sender addresses carefully",
            "Look for spelling and grammar errors",
            "Don't click on suspicious links",
            "Use two-factor authentication when possible",
            "Keep your software and systems updated",
            "Report suspicious activities to relevant authorities"
        ]
    }
