"""
api_charts.py — Convenience wrappers that combine data extraction + chart rendering.
Pages import from here instead of calling charts.py directly with raw dicts.
"""
import plotly.graph_objects as go
from frontend.components.charts import (
    make_score_gauge,
    make_price_trend_chart,
    make_breakdown_bar,
    make_radar_chart,
)


def score_gauge_from_result(result: dict) -> go.Figure:
    """Build score gauge directly from a full analyze API result dict."""
    score = result.get("confidence_score", {})
    return make_score_gauge(
        score.get("overall", 0),
        score.get("tier", "Hold"),
        score.get("tier_color", "#FACC15"),
    )


def price_trend_from_result(result: dict) -> go.Figure:
    """Build price trend chart directly from a full analyze API result dict."""
    return make_price_trend_chart(result.get("raw_data", {}))


def breakdown_bar_from_result(result: dict) -> go.Figure:
    """Build score breakdown bar chart from a full analyze API result dict."""
    score = result.get("confidence_score", {})
    return make_breakdown_bar(score.get("breakdown", {}))


def radar_from_result(result: dict) -> go.Figure:
    """Build market radar chart from a full analyze API result dict."""
    return make_radar_chart(result.get("market_signals", {}))


def compare_breakdown_charts(comparisons: list) -> list[go.Figure]:
    """
    Return a list of breakdown bar charts for each comparison result.
    Usage:
        figs = compare_breakdown_charts(comparisons)
        for fig in figs:
            st.plotly_chart(fig, use_container_width=True)
    """
    charts = []
    for comp in comparisons:
        score = comp.get("confidence_score", {})
        fig   = make_breakdown_bar(score.get("breakdown", {}))
        name  = comp.get("neighborhood", "")
        fig.update_layout(title=dict(
            text=(
                f"<span style='font-family:DM Mono;font-size:10px;"
                f"color:#44445A;letter-spacing:1px'>{name.upper()}</span>"
            ),
            x=0,
        ))
        charts.append(fig)
    return charts


def all_charts_from_result(result: dict) -> dict[str, go.Figure]:
    """
    Return all four charts for a result in one call.
    Usage:
        charts = all_charts_from_result(result)
        st.plotly_chart(charts["gauge"])
        st.plotly_chart(charts["trend"])
        st.plotly_chart(charts["breakdown"])
        st.plotly_chart(charts["radar"])
    """
    return {
        "gauge":     score_gauge_from_result(result),
        "trend":     price_trend_from_result(result),
        "breakdown": breakdown_bar_from_result(result),
        "radar":     radar_from_result(result),
    }