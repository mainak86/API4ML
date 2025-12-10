"""Empathy API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.empathy_service import EmpathyResponseGenerator, EmotionalTone
from app.core import get_session
from sqlmodel import Session

router = APIRouter(prefix="/api/empathy", tags=["empathy"])

# Global empathy generator instance
empathy_generator = None


def get_empathy_generator() -> EmpathyResponseGenerator:
    """Dependency to get empathy generator"""
    global empathy_generator
    if empathy_generator is None:
        empathy_generator = EmpathyResponseGenerator()
    return empathy_generator


class EmpathyRequest(BaseModel):
    """Request for empathetic response"""
    user_message: str
    conversation_history: list[dict] | None = None


class EmpathyResponse(BaseModel):
    """Response with empathetic message"""
    response: str
    emotional_tone: str
    empathy_score: float
    context: str


class ConversationSummaryRequest(BaseModel):
    """Request for conversation emotional summary"""
    conversation_history: list[dict]


class ConversationSummary(BaseModel):
    """Emotional summary of conversation"""
    sentiment: str
    emotional_journey: str
    key_concerns: list[str]
    empathy_level_needed: float
    recommendation: str


@router.post("/response", response_model=EmpathyResponse)
async def get_empathetic_response(
    request: EmpathyRequest,
    generator: EmpathyResponseGenerator = Depends(get_empathy_generator)
):
    """
    Get an empathetic AI response to user message.
    
    Uses LangGraph workflow to:
    1. Analyze emotional tone
    2. Detect context
    3. Generate empathy
    4. Create response
    5. Enhance with empathy
    """
    try:
        # Generate empathetic response
        response = await generator.generate_empathetic_response(
            user_message=request.user_message,
            conversation_history=request.conversation_history
        )
        
        # Analyze emotions for metadata
        analysis = await generator.analyzer.analyze_emotional_tone(request.user_message)
        
        return EmpathyResponse(
            response=response,
            emotional_tone=analysis.get("tone", "neutral"),
            empathy_score=float(analysis.get("empathy_score", 0.5)),
            context=analysis.get("context", "general conversation")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_emotional_tone(
    request: EmpathyRequest,
    generator: EmpathyResponseGenerator = Depends(get_empathy_generator)
):
    """
    Analyze emotional tone of a message.
    
    Returns:
    - tone: detected emotional tone
    - empathy_score: how much empathy is needed (0-1)
    - context: what user is dealing with
    - keywords: emotional keywords found
    """
    try:
        analysis = await generator.analyzer.analyze_emotional_tone(request.user_message)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary", response_model=ConversationSummary)
async def get_conversation_summary(
    request: ConversationSummaryRequest,
    generator: EmpathyResponseGenerator = Depends(get_empathy_generator)
):
    """
    Get emotional summary of entire conversation.
    
    Returns:
    - sentiment: overall sentiment
    - emotional_journey: how user's emotions evolved
    - key_concerns: main issues raised
    - empathy_level_needed: recommended empathy level going forward
    - recommendation: how to support user best
    """
    try:
        summary = await generator.get_emotional_summary(request.conversation_history)
        return ConversationSummary(
            sentiment=summary.get("sentiment", "neutral"),
            emotional_journey=summary.get("emotional_journey", ""),
            key_concerns=summary.get("key_concerns", []),
            empathy_level_needed=float(summary.get("empathy_level_needed", 0.5)),
            recommendation=summary.get("recommendation", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tones")
async def get_available_emotional_tones():
    """Get list of available emotional tones"""
    return {
        "available_tones": [tone.value for tone in EmotionalTone],
        "descriptions": {
            "positive": "User is happy, satisfied, or enthusiastic",
            "negative": "User is unhappy or dissatisfied",
            "neutral": "User is matter-of-fact",
            "frustrated": "User is annoyed or irritated",
            "anxious": "User is worried or nervous",
            "confused": "User is unsure or unclear",
            "excited": "User is enthusiastic or energized",
        }
    }
