from pydantic import BaseModel
from typing import Optional, List, Dict, Any


# ── Requests ──────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    neighborhood: str
    city: str = ""


class ChatRequest(BaseModel):
    query: str
    neighborhood: str
    city: str = ""
    chat_history: List[Dict[str, str]] = []
    # Pass prior analysis results to avoid re-running
    raw_data: Optional[Dict[str, Any]] = None
    market_signals: Optional[Dict[str, Any]] = None
    confidence_score: Optional[Dict[str, Any]] = None
    report: Optional[str] = None


class CompareRequest(BaseModel):
    neighborhoods: List[AnalyzeRequest]


# ── Responses ─────────────────────────────────────────────
class ConfidenceScoreResponse(BaseModel):
    overall: float
    breakdown: Dict[str, float]
    tier: str
    tier_color: str
    explanation: str


class AnalyzeResponse(BaseModel):
    neighborhood: str
    city: str
    raw_data: Dict[str, Any]
    market_signals: Dict[str, Any]
    confidence_score: ConfidenceScoreResponse
    report: str
    report_bullets: List[str]
    sources: List[str]
    processing_steps: List[str]


class ChatResponse(BaseModel):
    response: str
    chat_history: List[Dict[str, str]]


class HealthResponse(BaseModel):
    status: str
    version: str