
"""Tests for the LangGraph agent pipeline."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.agent.nodes.data_fetcher import data_fetcher_node
from backend.agent.nodes.analyzer import analyzer_node
from backend.agent.nodes.scorer import scorer_node


def base_state(neighborhood="Leslieville", city="Toronto"):
    return {
        "neighborhood": neighborhood,
        "city": city,
        "processing_steps": [],
        "sources": [],
        "chat_history": [],
    }


def test_data_fetcher_known():
    state  = data_fetcher_node(base_state("Leslieville", "Toronto"))
    raw    = state["raw_data"]
    assert raw["neighborhood"] == "Leslieville"
    assert raw["median_price"] > 0
    assert "avg_days_on_market" in raw


def test_data_fetcher_unknown():
    state = data_fetcher_node(base_state("Nowhere Special", "Atlantis"))
    raw   = state["raw_data"]
    # Should return synthetic fallback, not crash
    assert raw["median_price"] > 0


def test_analyzer_produces_signals():
    state   = data_fetcher_node(base_state())
    state   = analyzer_node(state)
    signals = state["market_signals"]
    assert 0 <= signals["demand_score"] <= 100
    assert 0 <= signals["supply_score"] <= 100
    assert -1 <= signals["price_momentum"] <= 1
    assert isinstance(signals["risk_flags"], list)
    assert isinstance(signals["positive_signals"], list)


def test_scorer_produces_valid_score():
    state = data_fetcher_node(base_state())
    state = analyzer_node(state)
    state = scorer_node(state)
    score = state["confidence_score"]
    assert 0 <= score["overall"] <= 100
    assert score["tier"] in ["Strong Buy", "Buy", "Hold", "Caution", "Avoid"]
    assert score["tier_color"].startswith("#")
    assert len(score["breakdown"]) == 6


def test_full_pipeline_no_llm():
    """Test nodes 1-3 (no LLM required)."""
    state = base_state("Liberty Village", "Toronto")
    state = data_fetcher_node(state)
    state = analyzer_node(state)
    state = scorer_node(state)

    assert state["confidence_score"]["overall"] > 0
    assert len(state["processing_steps"]) >= 3