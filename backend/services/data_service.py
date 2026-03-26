"""
Data service — aggregates neighborhood data from all available sources.
Orchestrates mock data, RapidAPI, and Brave Search into one unified dict.
"""
from typing import Dict, Any, List
from backend.agent.tools.real_estate import fetch_neighborhood_data
from backend.agent.tools.brave_search import search_neighborhood_news, compute_news_sentiment


def get_neighborhood_data(neighborhood: str, city: str) -> Dict[str, Any]:
    """
    Fetch and aggregate all data for a neighborhood.
    Returns unified data dict ready for the analyzer node.
    """
    # Core real estate data
    data = fetch_neighborhood_data(neighborhood, city)

    # Enrich with news sentiment if Brave key available
    news = search_neighborhood_news(neighborhood, city)
    sentiment = compute_news_sentiment(news)

    data["news_articles"] = news
    data["news_sentiment"] = sentiment

    return data


def get_market_comparison(neighborhoods: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Fetch data for multiple neighborhoods for comparison."""
    results = []
    for n in neighborhoods:
        try:
            data = get_neighborhood_data(n["neighborhood"], n["city"])
            results.append(data)
        except Exception as e:
            results.append({
                "neighborhood": n["neighborhood"],
                "city": n["city"],
                "error": str(e),
            })
    return results


def normalize_price(price: float, city: str) -> str:
    """Format price as human-readable string."""
    if price >= 1_000_000:
        return f"${price / 1_000_000:.2f}M"
    elif price >= 1_000:
        return f"${price / 1_000:.0f}K"
    return f"${price:,.0f}"


def get_city_benchmarks() -> Dict[str, Dict[str, float]]:
    """Return benchmark stats per city for comparison context."""
    return {
        "Toronto": {
            "median_price":       1_100_000,
            "price_change_1y":    4.5,
            "avg_days_on_market": 16,
            "rental_yield":       4.2,
        },
        "New York": {
            "median_price":       950_000,
            "price_change_1y":    3.8,
            "avg_days_on_market": 22,
            "rental_yield":       4.0,
        },
        "Miami": {
            "median_price":       680_000,
            "price_change_1y":    9.2,
            "avg_days_on_market": 14,
            "rental_yield":       5.5,
        },
        "San Francisco": {
            "median_price":       1_400_000,
            "price_change_1y":    -0.5,
            "avg_days_on_market": 24,
            "rental_yield":       3.1,
        },
    }