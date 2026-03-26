from backend.agent.state import AgentState


WEIGHTS = {
    "price_momentum":  0.25,
    "demand_score":    0.25,
    "supply_score":    0.15,
    "liquidity_score": 0.15,
    "rental_yield":    0.10,
    "walkability":     0.10,
}

TIERS = [
    (85, "Strong Buy",  "#00C896"),
    (70, "Buy",         "#4ADE80"),
    (55, "Hold",        "#FACC15"),
    (40, "Caution",     "#FB923C"),
    (0,  "Avoid",       "#F87171"),
]


def scorer_node(state: AgentState) -> AgentState:
    """Node 3: Compute weighted confidence score (0–100)."""
    steps = state.get("processing_steps", [])
    steps.append("🧮 Computing confidence score...")

    signals = state.get("market_signals", {})
    raw = state.get("raw_data", {})

    # Normalize all inputs to 0-100
    momentum_raw = signals.get("price_momentum", 0)            # -1 to 1
    momentum_norm = round((momentum_raw + 1) * 50, 1)          # → 0-100

    demand_norm    = signals.get("demand_score", 50)
    supply_norm    = signals.get("supply_score", 50)
    liquidity_norm = signals.get("liquidity_score", 50)

    rental_yield   = raw.get("rental_yield", 4.0)
    rental_norm    = min(100, (rental_yield / 8) * 100)         # 8%+ = 100

    walk  = raw.get("walk_score", 70)
    trans = raw.get("transit_score", 70)
    walk_norm = (walk * 0.6 + trans * 0.4)

    breakdown = {
        "Price Momentum":  round(momentum_norm * WEIGHTS["price_momentum"], 2),
        "Demand":          round(demand_norm    * WEIGHTS["demand_score"],   2),
        "Supply Tightness":round(supply_norm    * WEIGHTS["supply_score"],   2),
        "Liquidity":       round(liquidity_norm * WEIGHTS["liquidity_score"],2),
        "Rental Yield":    round(rental_norm    * WEIGHTS["rental_yield"],   2),
        "Walkability":     round(walk_norm      * WEIGHTS["walkability"],    2),
    }

    # Risk flag penalty
    n_risks = len(signals.get("risk_flags", []))
    risk_penalty = n_risks * 3

    overall = sum(breakdown.values()) - risk_penalty
    overall = round(max(0, min(100, overall)), 1)

    # Tier
    tier, tier_color = "Hold", "#FACC15"
    for threshold, label, color in TIERS:
        if overall >= threshold:
            tier, tier_color = label, color
            break

    explanation = _build_explanation(overall, tier, breakdown, n_risks)

    confidence_score = {
        "overall": overall,
        "breakdown": breakdown,
        "tier": tier,
        "tier_color": tier_color,
        "explanation": explanation,
    }

    steps.append(f"✅ Confidence score: {overall}/100 — {tier}")

    return {**state, "confidence_score": confidence_score, "processing_steps": steps}


def _build_explanation(score: float, tier: str, breakdown: dict, n_risks: int) -> str:
    top_factor = max(breakdown, key=breakdown.get)
    bottom_factor = min(breakdown, key=breakdown.get)
    risk_note = f" {n_risks} risk flag(s) reduced the score." if n_risks > 0 else ""
    return (
        f"This neighborhood scored {score}/100 ({tier}). "
        f"Strongest contributor: {top_factor}. "
        f"Weakest area: {bottom_factor}.{risk_note}"
    )