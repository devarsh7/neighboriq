"""
Real estate data fetcher.
Uses RapidAPI if key is set, otherwise falls back to mock data.
"""
import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

MOCK_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "mock" / "neighborhoods.json"

# RapidAPI endpoint (Realty Mole Property API as example)
RAPIDAPI_HOST    = "realty-mole-property-api.p.rapidapi.com"
RAPIDAPI_BASE    = f"https://{RAPIDAPI_HOST}"


def _load_mock() -> Dict:
    with open(MOCK_DATA_PATH) as f:
        return json.load(f)


def _fuzzy_key(neighborhood: str, city: str, keys: list) -> Optional[str]:
    query = f"{neighborhood}, {city}".lower().strip()
    for k in keys:
        if query == k:
            return k
    for k in keys:
        if neighborhood.lower() in k or k.split(",")[0].strip() in neighborhood.lower():
            return k
    return None


def fetch_neighborhood_data(neighborhood: str, city: str) -> Dict[str, Any]:
    """
    Primary data fetch function.
    Tries RapidAPI first, falls back to mock data.
    """
    api_key = os.environ.get("RAPIDAPI_KEY", "")
    if api_key:
        data = _fetch_from_rapidapi(neighborhood, city, api_key)
        if data:
            return data

    return _fetch_from_mock(neighborhood, city)


def _fetch_from_mock(neighborhood: str, city: str) -> Dict[str, Any]:
    mock = _load_mock()
    keys = list(mock["neighborhoods"].keys())
    key  = _fuzzy_key(neighborhood, city, keys)

    if key:
        return mock["neighborhoods"][key]

    # Synthetic fallback
    return {
        "neighborhood":      neighborhood.title(),
        "city":              city.title(),
        "country":           "Canada",
        "median_price":      950000,
        "price_change_1y":   3.5,
        "price_change_3y":   15.0,
        "avg_days_on_market": 18,
        "inventory_count":   55,
        "sold_last_30d":     40,
        "price_per_sqft":    750,
        "rental_yield":      4.2,
        "walk_score":        72,
        "transit_score":     68,
    }


def _fetch_from_rapidapi(neighborhood: str, city: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch live data from RapidAPI Realty Mole."""
    try:
        headers = {
            "X-RapidAPI-Key":  api_key,
            "X-RapidAPI-Host": RAPIDAPI_HOST,
        }
        params = {"city": city, "state": "ON", "limit": "10"}
        r = requests.get(
            f"{RAPIDAPI_BASE}/properties",
            headers=headers,
            params=params,
            timeout=10,
        )
        r.raise_for_status()
        listings = r.json()
        if not listings:
            return None

        prices = [l.get("price", 0) for l in listings if l.get("price")]
        if not prices:
            return None

        median_price = sorted(prices)[len(prices) // 2]
        return {
            "neighborhood":       neighborhood.title(),
            "city":               city.title(),
            "country":            "Canada",
            "median_price":       median_price,
            "price_change_1y":    3.0,   # RapidAPI free tier doesn't include YoY
            "price_change_3y":    12.0,
            "avg_days_on_market": 18,
            "inventory_count":    len(listings),
            "sold_last_30d":      int(len(listings) * 0.6),
            "price_per_sqft":     int(median_price / 1200),
            "rental_yield":       4.0,
            "walk_score":         75,
            "transit_score":      70,
        }
    except Exception as e:
        print(f"[RapidAPI] Error: {e}")
        return None


def get_available_neighborhoods() -> list:
    """Return list of all preloaded neighborhood names."""
    mock = _load_mock()
    return [
        f"{v['neighborhood']}, {v['city']}"
        for v in mock["neighborhoods"].values()
    ]