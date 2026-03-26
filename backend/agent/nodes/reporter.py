import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from backend.agent.state import AgentState


SYSTEM_PROMPT = """You are NeighborIQ, an elite real estate intelligence analyst. 
You write sharp, data-driven neighborhood reports for sophisticated buyers, investors, and operators.
Your tone is confident, direct, and insightful — like a top analyst at a prop-tech firm.
Never hedge unnecessarily. Lead with the most important insight.
Format: write in flowing paragraphs, not bullet points. 3-4 paragraphs max."""


def reporter_node(state: AgentState) -> AgentState:
    """Node 4: Generate AI narrative report using Claude."""
    steps = state.get("processing_steps", [])
    steps.append("✍️ Generating AI narrative report...")

    raw = state.get("raw_data", {})
    signals = state.get("market_signals", {})
    score = state.get("confidence_score", {})

    neighborhood = raw.get("neighborhood", "Unknown")
    city = raw.get("city", "Unknown")

    prompt = f"""
Generate a neighborhood intelligence report for **{neighborhood}, {city}**.

## Raw Data
- Median Price: ${raw.get('median_price', 0):,.0f}
- 1Y Price Change: {raw.get('price_change_1y', 0):+.1f}%
- 3Y Price Change: {raw.get('price_change_3y', 0):+.1f}%
- Avg Days on Market: {raw.get('avg_days_on_market', 0)}
- Inventory: {raw.get('inventory_count', 0)} listings
- Sold Last 30 Days: {raw.get('sold_last_30d', 0)}
- Price/sqft: ${raw.get('price_per_sqft', 0):,.0f}
- Rental Yield: {raw.get('rental_yield', 0):.1f}%
- Walk Score: {raw.get('walk_score', 0)} | Transit Score: {raw.get('transit_score', 0)}

## Market Signals
- Demand Score: {signals.get('demand_score', 0)}/100
- Supply Tightness: {signals.get('supply_score', 0)}/100
- Price Momentum: {signals.get('price_momentum', 0):+.2f}
- Liquidity Score: {signals.get('liquidity_score', 0)}/100
- Risk Flags: {', '.join(signals.get('risk_flags', ['None'])) or 'None'}
- Positive Signals: {', '.join(signals.get('positive_signals', ['None'])) or 'None'}

## Confidence Score
- Overall: {score.get('overall', 0)}/100 — {score.get('tier', 'N/A')}
- Score Explanation: {score.get('explanation', '')}

Write 3 concise paragraphs:
1. Market overview and current momentum
2. Key opportunities and risks for buyers/investors
3. Forward-looking outlook and recommendation

Be direct, specific, and analytical. Use the data.
"""

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            max_tokens=800,
        )
        response = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)])
        report_text = response.content
    except Exception as e:
        report_text = (
            f"{neighborhood}, {city} presents a {score.get('tier', 'moderate')} market opportunity "
            f"with a confidence score of {score.get('overall', 0)}/100. "
            f"Median prices sit at ${raw.get('median_price', 0):,.0f} with {raw.get('price_change_1y', 0):+.1f}% "
            f"year-over-year growth. {score.get('explanation', '')}"
        )
        steps.append(f"⚠️ LLM fallback used: {str(e)[:60]}")

    # Generate bullet summary
    bullets = _extract_bullets(raw, signals, score)

    steps.append("✅ Report generated")

    return {
        **state,
        "report": report_text,
        "report_bullets": bullets,
        "processing_steps": steps,
    }


def _extract_bullets(raw: dict, signals: dict, score: dict) -> list[str]:
    bullets = []
    p1y = raw.get("price_change_1y", 0)
    bullets.append(f"Median price: ${raw.get('median_price', 0):,.0f} ({p1y:+.1f}% YoY)")
    bullets.append(f"Avg {raw.get('avg_days_on_market', 0)} days on market — {'fast' if raw.get('avg_days_on_market', 20) < 14 else 'moderate'} velocity")
    bullets.append(f"Rental yield: {raw.get('rental_yield', 0):.1f}% — {'strong' if raw.get('rental_yield', 0) > 5 else 'average'} investor return")
    bullets.append(f"Walk Score {raw.get('walk_score', 0)} · Transit Score {raw.get('transit_score', 0)}")
    if signals.get("risk_flags"):
        bullets.append(f"{len(signals['risk_flags'])} risk flag(s) identified")
    return bullets