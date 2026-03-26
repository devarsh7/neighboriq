import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from backend.agent.state import AgentState


def qa_agent_node(state: AgentState) -> AgentState:
    """Node 5: Answer follow-up questions about the neighborhood."""
    steps = state.get("processing_steps", [])

    raw      = state.get("raw_data", {})
    signals  = state.get("market_signals", {})
    score    = state.get("confidence_score", {})
    report   = state.get("report", "")
    history  = state.get("chat_history", [])
    query    = state.get("query", "")

    if not query:
        return {**state, "chat_response": "Please ask a question about this neighborhood."}

    context = f"""
You are NeighborIQ, an expert real estate analyst. You have already analyzed {raw.get('neighborhood')}, {raw.get('city')}.

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

YOUR REPORT:
{report}

Answer concisely and specifically. Reference the data. Be the smartest analyst in the room.
"""

    messages = [SystemMessage(content=context)]
    for h in history[-6:]:  # last 3 turns
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        else:
            messages.append(AIMessage(content=h["content"]))
    messages.append(HumanMessage(content=query))

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
            max_tokens=400,
        )
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        answer = f"I encountered an issue: {str(e)[:80]}. Please check your API key."

    updated_history = history + [
        {"role": "user", "content": query},
        {"role": "assistant", "content": answer},
    ]

    return {**state, "chat_response": answer, "chat_history": updated_history, "processing_steps": steps}