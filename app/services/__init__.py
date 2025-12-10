"""Services module."""
from app.services.ai_service import get_ai_response
from app.services.rag_service import get_rag_response, get_rag_response_with_conversation
from app.services.guardrails_service import (
    validate_all_guardrails,
    check_sensitivity,
    check_toxicity,
    check_data_loss_prevention,
    check_data_privacy,
)

# Optional empathy support - disabled due to dependency conflicts
try:
    from app.services.empathy_service import EmpathyResponseGenerator, EmotionalTone, EmpathyAnalyzer
    EMPATHY_AVAILABLE = True
except (ImportError, RuntimeError):
    EMPATHY_AVAILABLE = False
    EmpathyResponseGenerator = None
    EmotionalTone = None
    EmpathyAnalyzer = None

__all__ = [
    "get_ai_response",
    "get_rag_response",
    "get_rag_response_with_conversation",
    "validate_all_guardrails",
    "check_sensitivity",
    "check_toxicity",
    "check_data_loss_prevention",
    "check_data_privacy",
    "EmpathyResponseGenerator",
    "EmotionalTone",
    "EmpathyAnalyzer",
    "EMPATHY_AVAILABLE",
]
