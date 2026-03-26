from typing import TypedDict, Optional, List, Dict, Any


class NeighborhoodData(TypedDict, total=False):
    neighborhood: str
    city: str
    country: str
    median_price: float
    price_change_1y: float
    price_change_3y: float
    avg_days_on_market: int
    inventory_count: int
    sold_last_30d: int
    price_per_sqft: float
    rental_yield: float
    walk_score: int
    transit_score: int


class MarketSignals(TypedDict, total=False):
    demand_score: float        # 0-100
    supply_score: float        # 0-100
    price_momentum: float      # -1 to 1
    liquidity_score: float     # 0-100
    risk_flags: List[str]
    positive_signals: List[str]
    news_sentiment: float      # -1 to 1
    recent_news: List[Dict[str, str]]


class ConfidenceScore(TypedDict, total=False):
    overall: float             # 0-100
    breakdown: Dict[str, float]
    tier: str                  # "Strong Buy", "Buy", "Hold", "Caution", "Avoid"
    tier_color: str
    explanation: str


class AgentState(TypedDict, total=False):
    # Input
    neighborhood: str
    city: str
    query: str                 # for Q&A mode

    # Pipeline data
    raw_data: NeighborhoodData
    market_signals: MarketSignals
    confidence_score: ConfidenceScore
    report: str
    report_bullets: List[str]

    # Q&A
    chat_history: List[Dict[str, str]]
    chat_response: str

    # Meta
    error: Optional[str]
    sources: List[str]
    processing_steps: List[str]