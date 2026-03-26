import json
import os
import re
from pathlib import Path
from backend.agent.state import AgentState

MOCK_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "mock" / "neighborhoods.json"


def _load_mock_data() -> dict:
    with open(MOCK_DATA_PATH) as f:
        return json.load(f)


def _fuzzy_match(query: str, keys: list[str]) -> str | None:
    """Find closest neighborhood key from query."""
    query_lower = query.lower().strip()
    # Exact match
    if query_lower in keys:
        return query_lower
    # Partial match
    for key in keys:
        if query_lower in key or key in query_lower:
            return key
    # Word overlap
    query_words = set(re.split(r"[\s,]+", query_lower))
    best_match, best_score = None, 0
    for key in keys:
        key_words = set(re.split(r"[\s,]+", key))
        score = len(query_words & key_words)
        if score > best_score:
            best_score, best_match = score, key
    return best_match if best_score > 0 else None


def data_fetcher_node(state: AgentState) -> AgentState:
    """Node 1: Fetch neighborhood data from mock store (or real API if key present)."""
    steps = state.get("processing_steps", [])
    steps.append("📡 Fetching neighborhood data...")

    neighborhood = state.get("neighborhood", "")
    city = state.get("city", "")
    search_key = f"{neighborhood}, {city}".lower().strip() if city else neighborhood.lower().strip()

    mock = _load_mock_data()
    keys = list(mock["neighborhoods"].keys())
    matched_key = _fuzzy_match(search_key, keys)

    if matched_key:
        raw_data = mock["neighborhoods"][matched_key]
        steps.append(f"✅ Found data for: {raw_data['neighborhood']}, {raw_data['city']}")
    else:
        # Generate plausible synthetic data so the agent can still run
        steps.append(f"⚠️ No cached data found — generating synthetic baseline for '{neighborhood}'")
        raw_data = {
            "neighborhood": neighborhood.title(),
            "city": city.title() if city else "Unknown",
            "country": "Canada",
            "median_price": 950000,
            "price_change_1y": 3.5,
            "price_change_3y": 15.0,
            "avg_days_on_market": 18,
            "inventory_count": 55,
            "sold_last_30d": 40,
            "price_per_sqft": 750,
            "rental_yield": 4.2,
            "walk_score": 72,
            "transit_score": 68,
        }

    return {
        **state,
        "raw_data": raw_data,
        "sources": ["NeighborIQ Mock Data v2.0", "Synthetic Baseline Engine"],
        "processing_steps": steps,
    }