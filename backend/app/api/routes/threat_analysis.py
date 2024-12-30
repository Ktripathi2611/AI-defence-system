from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from pydantic import BaseModel, HttpUrl
from backend.app.services.threat_analysis import threat_analysis_service
from backend.app.core.security import get_current_user

router = APIRouter()

class URLAnalysisRequest(BaseModel):
    url: HttpUrl
    metadata: dict = {}

class FileAnalysisRequest(BaseModel):
    file_content: bytes
    file_name: str
    metadata: dict = {}

class ThreatAnalysisResponse(BaseModel):
    is_malicious: bool
    threat_type: str = None
    confidence: float
    details: dict = {}
    safety_recommendations: List[str] = []

@router.post("/analyze/url", response_model=ThreatAnalysisResponse)
async def analyze_url(request: URLAnalysisRequest, current_user = Depends(get_current_user)):
    """
    Analyze a URL for potential threats
    """
    try:
        result = await threat_analysis_service.analyze_url(str(request.url), request.metadata)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/file", response_model=ThreatAnalysisResponse)
async def analyze_file(request: FileAnalysisRequest, current_user = Depends(get_current_user)):
    """
    Analyze a file for potential threats
    """
    try:
        result = await threat_analysis_service.analyze_file(
            request.file_content,
            request.file_name,
            request.metadata
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=Dict[str, int])
async def get_threat_stats(current_user = Depends(get_current_user)):
    """
    Get statistics about analyzed threats
    """
    try:
        return await threat_analysis_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
