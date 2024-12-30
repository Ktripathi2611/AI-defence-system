from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict
from pydantic import BaseModel
from backend.app.services.user_awareness import user_awareness_service
from backend.app.core.security import get_current_user

router = APIRouter()

class SecurityTip(BaseModel):
    title: str
    description: str
    category: str
    severity: str

class LearningModule(BaseModel):
    title: str
    content: str
    category: str
    difficulty_level: str

@router.get("/tips", response_model=List[SecurityTip])
async def get_security_tips(current_user = Depends(get_current_user)):
    """
    Get a list of security tips
    """
    try:
        return await user_awareness_service.get_security_tips()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/modules", response_model=List[LearningModule])
async def get_learning_modules(current_user = Depends(get_current_user)):
    """
    Get available learning modules
    """
    try:
        return await user_awareness_service.get_learning_modules()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quiz/{module_id}")
async def get_module_quiz(module_id: str, current_user = Depends(get_current_user)):
    """Get quiz questions for a specific learning module"""
    try:
        quiz = await user_awareness_service.get_security_quiz(module_id)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples")
async def get_real_world_examples(current_user = Depends(get_current_user)):
    """Get real-world examples of cyber threats"""
    try:
        examples = await user_awareness_service.get_real_world_examples()
        return {"examples": examples}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resources", response_model=Dict[str, List[str]])
async def get_emergency_resources(current_user = Depends(get_current_user)):
    """
    Get emergency resources and contacts
    """
    try:
        return await user_awareness_service.get_emergency_resources()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
