"""
Filesystem tool — save and load neighborhood reports locally.
Mirrors what the MCP filesystem server would do, works standalone too.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

REPORTS_DIR = Path(__file__).parent.parent.parent / "data" / "reports"


def _ensure_dir():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _report_key(neighborhood: str, city: str) -> str:
    return f"{neighborhood.lower().replace(' ', '_')}_{city.lower().replace(' ', '_')}"


def save_report(
    neighborhood: str,
    city: str,
    raw_data: Dict,
    market_signals: Dict,
    confidence_score: Dict,
    report_text: str,
    bullets: List[str],
) -> str:
    """Persist a full analysis result to disk. Returns the file path."""
    _ensure_dir()
    key       = _report_key(neighborhood, city)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{key}_{timestamp}.json"
    filepath  = REPORTS_DIR / filename

    payload = {
        "neighborhood":    neighborhood,
        "city":            city,
        "saved_at":        datetime.now().isoformat(),
        "raw_data":        raw_data,
        "market_signals":  market_signals,
        "confidence_score": confidence_score,
        "report":          report_text,
        "report_bullets":  bullets,
    }

    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)

    return str(filepath)


def load_report(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a saved report from disk."""
    try:
        with open(filepath) as f:
            return json.load(f)
    except Exception as e:
        print(f"[Filesystem] Could not load {filepath}: {e}")
        return None


def list_saved_reports() -> List[Dict[str, Any]]:
    """Return metadata for all saved reports, newest first."""
    _ensure_dir()
    reports = []
    for f in sorted(REPORTS_DIR.glob("*.json"), reverse=True):
        try:
            with open(f) as fh:
                data = json.load(fh)
            reports.append({
                "filename":     f.name,
                "filepath":     str(f),
                "neighborhood": data.get("neighborhood", ""),
                "city":         data.get("city", ""),
                "saved_at":     data.get("saved_at", ""),
                "score":        data.get("confidence_score", {}).get("overall", 0),
                "tier":         data.get("confidence_score", {}).get("tier", ""),
            })
        except Exception:
            continue
    return reports


def delete_report(filepath: str) -> bool:
    """Delete a saved report. Returns True on success."""
    try:
        os.remove(filepath)
        return True
    except Exception:
        return False