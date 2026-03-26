"""
Brave Search tool wrapper.
Uses direct REST API if BRAVE_API_KEY is set, else returns empty results gracefully.
"""
import os
import requests
from typing import List, Dict


BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


def brave_search(query: str, count: int = 5) -> List[Dict[str, str]]:
    """
    Search for real estate news/signals using Brave Search API.
    Returns list of {title, url, description} dicts.
    Falls back to empty list if API key not set.
    """
    api_key = os.environ.get("BRAVE_API_KEY", "")
    if not api_key:
        return []

    try:
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        }
        params = {"q": query, "count": count, "search_lang": "en"}
        response = requests.get(BRAVE_ENDPOINT, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title":       item.get("title", ""),
                "url":         item.get("url", ""),
                "description": item.get("description", ""),
            })
        return results

    except Exception as e:
        print(f"[BraveSearch] Error: {e}")
        return []


def search_neighborhood_news(neighborhood: str, city: str) -> List[Dict[str, str]]:
    """Convenience wrapper — searches for recent real estate news for a neighborhood."""
    query = f"{neighborhood} {city} real estate market 2025"
    return brave_search(query, count=5)


def search_market_trends(city: str) -> List[Dict[str, str]]:
    """Search for broader city-level market trends."""
    query = f"{city} housing market trends prices 2025"
    return brave_search(query, count=4)


def compute_news_sentiment(articles: List[Dict[str, str]]) -> float:
    """
    Simple keyword-based sentiment score from article descriptions.
    Returns float from -1.0 (bearish) to 1.0 (bullish).
    """
    if not articles:
        return 0.0

    positive_keywords = [
        "surge", "rise", "growth", "demand", "hot", "boom", "increase",
        "strong", "record", "high", "gain", "up", "bullish", "opportunity",
    ]
    negative_keywords = [
        "decline", "drop", "fall", "slow", "crash", "risk", "concern",
        "down", "bearish", "weak", "low", "loss", "struggle", "correction",
    ]

    score = 0.0
    total = 0
    for article in articles:
        text = (article.get("title", "") + " " + article.get("description", "")).lower()
        for kw in positive_keywords:
            if kw in text:
                score += 1
                total += 1
        for kw in negative_keywords:
            if kw in text:
                score -= 1
                total += 1

    if total == 0:
        return 0.0
    return round(max(-1.0, min(1.0, score / total)), 3)