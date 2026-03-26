import os
from anthropic import Anthropic
from backend.agent.state import AgentState


def reporter_node(state: AgentState) -> AgentState:
    """Node 4: Generate AI narrative report using Anthropic SDK directly."""
    steps = state.get("processing_steps", [])
    steps.append("✍️ Generating AI narrative report...")

    raw     = state.get("raw_data", {})
    signals = state.get("market_signals", {})
    score   = state.get("confidence_score", {})

    neighborhood = raw.get("neighborhood", "Unknown")
    city         = raw.get("city", "Unknown")

    prompt = f"""Generate a neighborhood intelligence report for {neighborhood}, {city}.

MARKET DATA:
- Median Price: ${raw.get('median_price', 0):,.0f}
- 1Y Price Change: {raw.get('price_change_1y', 0):+.1f}%
- 3Y Price Change: {raw.get('price_change_3y', 0):+.1f}%
- Avg Days on Market: {raw.get('avg_days_on_market', 0)}
- Inventory: {raw.get('inventory_count', 0)} listings
- Sold Last 30 Days: {raw.get('sold_last_30d', 0)}
- Price/sqft: ${raw.get('price_per_sqft', 0):,.0f}
- Rental Yield: {raw.get('rental_yield', 0):.1f}%
- Walk Score: {raw.get('walk_score', 0)} | Transit Score: {raw.get('transit_score', 0)}

SIGNALS:
- Demand Score: {signals.get('demand_score', 0)}/100
- Supply Tightness: {signals.get('supply_score', 0)}/100
- Price Momentum: {signals.get('price_momentum', 0):+.2f}
- Risk Flags: {', '.join(signals.get('risk_flags', ['None']))}
- Positive Signals: {', '.join(signals.get('positive_signals', ['None']))}

CONFIDENCE SCORE: {score.get('overall', 0)}/100 — {score.get('tier', 'N/A')}

Write 3 concise paragraphs:
1. Market overview and current momentum
2. Key opportunities and risks for buyers/investors
3. Forward-looking outlook and recommendation

Be direct, specific, analytical. Use the data. No fluff."""

    try:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        resp   = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            system="You are NeighborIQ, an elite real estate intelligence analyst. Write sharp, data-driven neighborhood reports. Confident, direct, no hedging.",
            messages=[{"role": "user", "content": prompt}],
        )
        report_text = resp.content[0].text
        steps.append("✅ Report generated")
    except Exception as e:
        report_text = (
            f"{neighborhood}, {city} shows a {score.get('tier','moderate')} market "
            f"with a confidence score of {score.get('overall',0)}/100. "
            f"Median prices at ${raw.get('median_price',0):,.0f} with "
            f"{raw.get('price_change_1y',0):+.1f}% year-over-year growth."
        )
        steps.append(f"⚠️ LLM fallback used: {str(e)[:80]}")

    bullets = _extract_bullets(raw, signals, score)

    return {
        **state,
        "report": report_text,
        "report_bullets": bullets,
        "processing_steps": steps,
    }


def _extract_bullets(raw: dict, signals: dict, score: dict) -> list:
    p1y = raw.get("price_change_1y", 0)
    dom = raw.get("avg_days_on_market", 0)
    rent= raw.get("rental_yield", 0)
    return [
        f"Median price: ${raw.get('median_price',0):,.0f} ({p1y:+.1f}% YoY)",
        f"Avg {dom} days on market — {'fast' if dom < 14 else 'moderate' if dom < 22 else 'slow'} velocity",
        f"Rental yield: {rent:.1f}% — {'strong' if rent > 5 else 'average'} investor return",
        f"Walk Score {raw.get('walk_score',0)} · Transit Score {raw.get('transit_score',0)}",
        f"{len(signals.get('risk_flags',[]))} risk flag(s) identified",
    ]