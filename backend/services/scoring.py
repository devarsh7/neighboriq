"""
Standalone confidence score service.
Can be called directly without going through the full agent pipeline.
"""
from typing import Dict, Any

WEIGHTS = {
    "price_momentum":  0.25,
    "demand_score":    0.25,
    "supply_score":    0.15,
    "liquidity_score": 0.15,
    "rental_yield":    0.10,
    "walkability":     0.10,
}

TIERS = [
    (85, "Strong Buy", "#00C896"),
    (70, "Buy",        "#4ADE80"),
    (55, "Hold",       "#FACC15"),
    (40, "Caution",    "#FB923C"),
    (0,  "Avoid",      "#F87171"),
]


def compute_confidence_score(raw_data: Dict[str, Any], market_signals: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compute weighted confidence score from raw neighborhood data and market signals.
    Returns dict with overall score, breakdown, tier, color, explanation.
    """
    momentum_raw  = market_signals.get("price_momentum", 0)
    momentum_norm = round((momentum_raw + 1) * 50, 1)

    demand_norm    = market_signals.get("demand_score", 50)
    supply_norm    = market_signals.get("supply_score", 50)
    liquidity_norm = market_signals.get("liquidity_score", 50)

    rental_yield = raw_data.get("rental_yield", 4.0)
    rental_norm  = min(100, (rental_yield / 8) * 100)

    walk  = raw_data.get("walk_score", 70)
    trans = raw_data.get("transit_score", 70)
    walk_norm = walk * 0.6 + trans * 0.4

    breakdown = {
        "Price Momentum":   round(momentum_norm * WEIGHTS["price_momentum"],  2),
        "Demand":           round(demand_norm   * WEIGHTS["demand_score"],    2),
        "Supply Tightness": round(supply_norm   * WEIGHTS["supply_score"],    2),
        "Liquidity":        round(liquidity_norm * WEIGHTS["liquidity_score"], 2),
        "Rental Yield":     round(rental_norm   * WEIGHTS["rental_yield"],    2),
        "Walkability":      round(walk_norm     * WEIGHTS["walkability"],     2),
    }

    n_risks     = len(market_signals.get("risk_flags", []))
    risk_penalty = n_risks * 3
    overall     = round(max(0, min(100, sum(breakdown.values()) - risk_penalty)), 1)

    tier, color = "Hold", "#FACC15"
    for threshold, label, hex_color in TIERS:
        if overall >= threshold:
            tier, color = label, hex_color
            break

    top    = max(breakdown, key=breakdown.get)
    bottom = min(breakdown, key=breakdown.get)
    risk_note = f" {n_risks} risk flag(s) applied a penalty." if n_risks else ""
    explanation = (
        f"Scored {overall}/100 ({tier}). "
        f"Strongest factor: {top}. Weakest: {bottom}.{risk_note}"
    )

    return {
        "overall":     overall,
        "breakdown":   breakdown,
        "tier":        tier,
        "tier_color":  color,
        "explanation": explanation,
    }


def score_to_label(score: float) -> str:
    for threshold, label, _ in TIERS:
        if score >= threshold:
            return label
    return "Avoid"


def score_to_color(score: float) -> str:
    for threshold, _, color in TIERS:
        if score >= threshold:
            return color
    return "#F87171"