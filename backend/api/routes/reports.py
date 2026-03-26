"""
reports.py — FastAPI routes for saving, listing, and deleting analysis reports.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from backend.services.report_service import (
    save_analysis,
    list_reports,
    get_report,
    delete_report,
)

router = APIRouter(prefix="/reports", tags=["reports"])


# ── Request / Response models ──────────────────────────────────────────────

class SaveReportRequest(BaseModel):
    neighborhood:     str
    city:             str
    raw_data:         Dict[str, Any]
    market_signals:   Dict[str, Any]
    confidence_score: Dict[str, Any]
    report:           str
    report_bullets:   List[str] = []


class ReportMetaResponse(BaseModel):
    filename:     str
    filepath:     str
    neighborhood: str
    city:         str
    saved_at:     str
    score:        float
    tier:         str


class DeleteResponse(BaseModel):
    success: bool
    message: str


# ── Routes ─────────────────────────────────────────────────────────────────

@router.post("/save", response_model=Dict[str, str])
async def save_report(req: SaveReportRequest):
    """Save a completed analysis result to disk."""
    try:
        filepath = save_analysis(req.model_dump())
        return {"filepath": filepath, "message": "Report saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[ReportMetaResponse])
async def list_all_reports():
    """Return metadata for all saved reports, newest first."""
    try:
        return list_reports()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{filepath:path}", response_model=Dict[str, Any])
async def get_single_report(filepath: str):
    """Load and return a full saved report by its filepath."""
    report = get_report(filepath)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report not found: {filepath}")
    return report


@router.delete("/{filepath:path}", response_model=DeleteResponse)
async def delete_single_report(filepath: str):
    """Delete a saved report by its filepath."""
    success = delete_report(filepath)
    if not success:
        raise HTTPException(status_code=404, detail=f"Could not delete: {filepath}")
    return DeleteResponse(success=True, message="Report deleted")