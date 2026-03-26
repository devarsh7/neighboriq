from backend.agent.state import AgentState


def analyzer_node(state: AgentState) -> AgentState:
    """Node 2: Compute market signals from raw data."""
    steps = state.get("processing_steps", [])
    steps.append("🔍 Analyzing market signals...")

    d = state.get("raw_data", {})

    # --- Demand Score (0-100) ---
    # Low days on market + high sold volume = high demand
    dom = d.get("avg_days_on_market", 20)
    dom_score = max(0, 100 - (dom * 3))  # 0 DOM = 100, 33+ DOM = 0

    sold = d.get("sold_last_30d", 30)
    inventory = d.get("inventory_count", 60)
    absorption = (sold / max(inventory, 1)) * 100
    absorption_score = min(100, absorption * 1.5)

    demand_score = round((dom_score * 0.5 + absorption_score * 0.5), 1)

    # --- Supply Score (0-100, lower = tighter supply = better for sellers) ---
    supply_tightness = max(0, 100 - min(100, inventory / 2))
    supply_score = round(supply_tightness, 1)

    # --- Price Momentum (-1 to 1) ---
    p1y = d.get("price_change_1y", 0)
    p3y = d.get("price_change_3y", 0)
    momentum = round(((p1y / 20) + (p3y / 60)) / 2, 3)
    momentum = max(-1, min(1, momentum))

    # --- Liquidity Score ---
    walk = d.get("walk_score", 70)
    transit = d.get("transit_score", 70)
    liquidity_score = round((walk * 0.4 + transit * 0.4 + absorption_score * 0.2), 1)

    # --- Risk Flags ---
    risk_flags = []
    positive_signals = []

    if p1y < 0:
        risk_flags.append("📉 Negative year-over-year price growth")
    if dom > 25:
        risk_flags.append("⏱️ High days-on-market suggests soft demand")
    if inventory > 80:
        risk_flags.append("📦 Elevated inventory — buyer's market conditions")
    if d.get("rental_yield", 4) < 3.5:
        risk_flags.append("🏦 Low rental yield may deter investors")
    if p3y < 10:
        risk_flags.append("📊 Below-average 3-year appreciation")

    if p1y > 5:
        positive_signals.append("🚀 Strong year-over-year price acceleration")
    if dom < 12:
        positive_signals.append("⚡ Homes selling fast — high buyer competition")
    if absorption > 80:
        positive_signals.append("🔥 High absorption rate — inventory being consumed quickly")
    if d.get("rental_yield", 0) > 5:
        positive_signals.append("💰 Above-average rental yield — strong investor appeal")
    if walk > 85:
        positive_signals.append("🚶 Excellent walkability boosts long-term value")
    if p3y > 25:
        positive_signals.append("📈 Exceptional 3-year appreciation trajectory")

    # --- News Sentiment (simulated — real integration via Brave MCP) ---
    # Derived from quantitative signals as proxy
    sentiment = round(momentum * 0.6 + (demand_score - 50) / 200, 3)
    sentiment = max(-1, min(1, sentiment))

    market_signals = {
        "demand_score": demand_score,
        "supply_score": supply_score,
        "price_momentum": momentum,
        "liquidity_score": round(liquidity_score, 1),
        "risk_flags": risk_flags,
        "positive_signals": positive_signals,
        "news_sentiment": sentiment,
        "recent_news": [],  # populated by Brave MCP tool
    }

    steps.append(f"✅ Signals computed — demand: {demand_score}, momentum: {momentum:+.2f}")

    return {**state, "market_signals": market_signals, "processing_steps": steps}