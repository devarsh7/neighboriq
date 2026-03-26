"""
Report service — high-level interface for saving and retrieving analysis reports.
Wraps the filesystem tool with business logic.
"""
from typing import Dict, Any, List, Optional
from backend.agent.tools.filesystem import (
    save_report as _save,
    load_report as _load,
    list_saved_reports as _list,
    delete_report as _delete,
)


def save_analysis(result: Dict[str, Any]) -> str:
    """
    Save a full analysis result dict (as returned by the agent pipeline).
    Returns filepath of saved report.
    """
    return _save(
        neighborhood   = result.get("neighborhood", ""),
        city           = result.get("city", ""),
        raw_data       = result.get("raw_data", {}),
        market_signals = result.get("market_signals", {}),
        confidence_score = result.get("confidence_score", {}),
        report_text    = result.get("report", ""),
        bullets        = result.get("report_bullets", []),
    )


def get_report(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a saved report by filepath."""
    return _load(filepath)


def list_reports() -> List[Dict[str, Any]]:
    """List all saved reports with metadata."""
    return _list()


def delete_report(filepath: str) -> bool:
    """Delete a report by filepath."""
    return _delete(filepath)


def format_report_summary(report_meta: Dict) -> str:
    """Format report metadata as a one-line summary string."""
    return (
        f"{report_meta['neighborhood']}, {report_meta['city']} — "
        f"Score: {report_meta['score']:.0f} ({report_meta['tier']}) — "
        f"Saved: {report_meta['saved_at'][:10]}"
    )