import httpx
import streamlit as st

BACKEND_URL = "http://localhost:8000"


def analyze(neighborhood: str, city: str) -> dict:
    try:
        r = httpx.post(
            f"{BACKEND_URL}/analyze",
            json={"neighborhood": neighborhood, "city": city},
            timeout=60.0,
        )
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        st.error("⚠️ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
        return {}
    except Exception as e:
        st.error(f"API error: {e}")
        return {}


def chat(query: str, session_data: dict, history: list) -> dict:
    try:
        payload = {
            "query": query,
            "neighborhood": session_data.get("neighborhood", ""),
            "city": session_data.get("city", ""),
            "chat_history": history,
            "raw_data": session_data.get("raw_data"),
            "market_signals": session_data.get("market_signals"),
            "confidence_score": session_data.get("confidence_score"),
            "report": session_data.get("report"),
        }
        r = httpx.post(f"{BACKEND_URL}/chat", json=payload, timeout=30.0)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"response": f"Error: {e}", "chat_history": history}


def compare(neighborhoods: list[dict]) -> dict:
    try:
        r = httpx.post(
            f"{BACKEND_URL}/analyze/compare",
            json={"neighborhoods": neighborhoods},
            timeout=90.0,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"comparisons": [], "error": str(e)}


def health_check() -> bool:
    try:
        r = httpx.get(f"{BACKEND_URL}/health", timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False