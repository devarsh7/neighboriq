"""Tests for the confidence scoring service."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from backend.services.scoring import compute_confidence_score, score_to_label, score_to_color


SAMPLE_RAW = {
    "median_price": 1120000,
    "price_change_1y": 6.8,
    "price_change_3y": 28.4,
    "avg_days_on_market": 10,
    "inventory_count": 28,
    "sold_last_30d": 31,
    "price_per_sqft": 820,
    "rental_yield": 4.4,
    "walk_score": 89,
    "transit_score": 78,
}

SAMPLE_SIGNALS = {
    "demand_score": 82.0,
    "supply_score": 86.0,
    "price_momentum": 0.45,
    "liquidity_score": 74.0,
    "risk_flags": [],
    "positive_signals": ["Strong demand", "Fast sales"],
    "news_sentiment": 0.3,
}


def test_score_in_range():
    result = compute_confidence_score(SAMPLE_RAW, SAMPLE_SIGNALS)
    assert 0 <= result["overall"] <= 100


def test_score_has_breakdown():
    result = compute_confidence_score(SAMPLE_RAW, SAMPLE_SIGNALS)
    assert len(result["breakdown"]) == 6
    assert all(v >= 0 for v in result["breakdown"].values())


def test_risk_penalty():
    signals_with_risks = {**SAMPLE_SIGNALS, "risk_flags": ["Risk A", "Risk B", "Risk C"]}
    score_no_risk   = compute_confidence_score(SAMPLE_RAW, SAMPLE_SIGNALS)["overall"]
    score_with_risk = compute_confidence_score(SAMPLE_RAW, signals_with_risks)["overall"]
    assert score_with_risk < score_no_risk


def test_score_to_label():
    assert score_to_label(90) == "Strong Buy"
    assert score_to_label(75) == "Buy"
    assert score_to_label(60) == "Hold"
    assert score_to_label(45) == "Caution"
    assert score_to_label(20) == "Avoid"


def test_score_to_color_returns_hex():
    color = score_to_color(75)
    assert color.startswith("#")
    assert len(color) == 7


def test_tier_field_present():
    result = compute_confidence_score(SAMPLE_RAW, SAMPLE_SIGNALS)
    assert result["tier"] in ["Strong Buy", "Buy", "Hold", "Caution", "Avoid"]
    assert result["tier_color"].startswith("#")
    assert len(result["explanation"]) > 10