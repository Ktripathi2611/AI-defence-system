from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from backend.app.services.community_reporting import community_reporting_service
from backend.app.core.security import get_current_user

router = APIRouter()

class ThreatReport(BaseModel):
    threat_type: str
    description: str
    url: Optional[str] = None
    file_hash: Optional[str] = None
    metadata: dict = {}

class ReportResponse(BaseModel):
    report_id: str
    status: str
    verification_score: float
    analysis_results: dict = {}

@router.post("/report", response_model=ReportResponse)
async def submit_report(report: ThreatReport, current_user = Depends(get_current_user)):
    """
    Submit a new threat report
    """
    try:
        return await community_reporting_service.submit_report(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    threat_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get list of submitted reports with optional filters
    """
    try:
        return await community_reporting_service.get_reports(threat_type, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_reporting_stats(current_user = Depends(get_current_user)):
    """
    Get statistics about community reports
    """
    try:
        return await community_reporting_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
