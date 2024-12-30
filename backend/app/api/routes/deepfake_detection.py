from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from pydantic import BaseModel
from backend.app.services.deepfake_detection import deepfake_detection_service
from backend.app.core.security import get_current_user

router = APIRouter()

class DeepfakeAnalysisResponse(BaseModel):
    is_deepfake: bool
    confidence: float
    detection_method: str
    artifacts_detected: List[str] = []
    safety_recommendations: List[str] = []

@router.post("/analyze/image", response_model=DeepfakeAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Analyze an image for potential deepfake manipulation
    """
    try:
        content = await file.read()
        result = await deepfake_detection_service.analyze_image(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/video", response_model=DeepfakeAnalysisResponse)
async def analyze_video(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Analyze a video for potential deepfake manipulation
    """
    try:
        content = await file.read()
        result = await deepfake_detection_service.analyze_video(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_detection_stats(current_user = Depends(get_current_user)):
    """
    Get statistics about deepfake detections
    """
    try:
        return await deepfake_detection_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
