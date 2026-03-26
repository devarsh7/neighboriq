import os
from anthropic import Anthropic
from backend.agent.state import AgentState


def qa_agent_node(state: AgentState) -> AgentState:
    """Node 5: Answer follow-up questions using Anthropic SDK directly."""
    steps  = state.get("processing_steps", [])
    raw    = state.get("raw_data", {})
    signals= state.get("market_signals", {})
    score  = state.get("confidence_score", {})
    report = state.get("report", "")
    history= state.get("chat_history", [])
    query  = state.get("query", "")

    if not query:
        return {**state, "chat_response": "Please ask a question about this neighborhood."}

    system = f"""You are NeighborIQ, an expert real estate analyst.
You have already analyzed {raw.get('neighborhood')}, {raw.get('city')}.

NEIGHBORHOOD DATA:
- Median Price: ${raw.get('median_price', 0):,.0f}
- 1Y Change: {raw.get('price_change_1y', 0):+.1f}% | 3Y: {raw.get('price_change_3y', 0):+.1f}%
- Days on Market: {raw.get('avg_days_on_market', 0)}
- Inventory: {raw.get('inventory_count', 0)} | Sold/30d: {raw.get('sold_last_30d', 0)}
- Price/sqft: ${raw.get('price_per_sqft', 0):,.0f}
- Rental Yield: {raw.get('rental_yield', 0):.1f}%
- Walk Score: {raw.get('walk_score', 0)} | Transit: {raw.get('transit_score', 0)}

CONFIDENCE SCORE: {score.get('overall', 0)}/100 — {score.get('tier', 'N/A')}
RISK FLAGS: {', '.join(signals.get('risk_flags', ['None']))}
POSITIVE SIGNALS: {', '.join(signals.get('positive_signals', ['None']))}

REPORT: {report}

Answer concisely. Reference the data. Be the smartest analyst in the room."""

    # Build messages — Anthropic SDK expects role: user | assistant only
    messages = []
    for h in history[-6:]:
        role = h.get("role", "user")
        if role == "ai":
            role = "assistant"
        messages.append({"role": role, "content": h["content"]})
    messages.append({"role": "user", "content": query})

    try:
        client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
        resp   = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=400,
            system=system,
            messages=messages,
        )
        answer = resp.content[0].text
    except Exception as e:
        answer = f"Error: {str(e)}"

    updated_history = history + [
        {"role": "user",      "content": query},
        {"role": "assistant", "content": answer},
    ]

    return {**state, "chat_response": answer, "chat_history": updated_history, "processing_steps": steps}