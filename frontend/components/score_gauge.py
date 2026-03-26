"""
Animated confidence score gauge component.
Renders the Plotly gauge chart for the confidence score.
"""
import plotly.graph_objects as go


def render_score_gauge(score: float, tier: str, color: str) -> go.Figure:
    """
    Returns a Plotly gauge figure for the confidence score.
    Usage:
        fig = render_score_gauge(78.5, "Buy", "#4ADE80")
        st.plotly_chart(fig, use_container_width=True)
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            "font": {"family": "Syne, sans-serif", "size": 52, "color": color},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickfont": {"family": "DM Mono, monospace", "size": 10, "color": "#44445A"},
                "tickvals": [0, 25, 50, 75, 100],
            },
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": "#13131f",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  40],  "color": "rgba(248,113,113,0.08)"},
                {"range": [40, 55],  "color": "rgba(251,146,60,0.08)"},
                {"range": [55, 70],  "color": "rgba(250,204,21,0.08)"},
                {"range": [70, 85],  "color": "rgba(74,222,128,0.08)"},
                {"range": [85, 100], "color": "rgba(0,200,150,0.12)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 2},
                "thickness": 0.75,
                "value": score,
            },
        },
        title={
            "text": (
                f"<span style='font-family:DM Mono;font-size:12px;"
                f"color:#44445A;letter-spacing:2px'>{tier.upper()}</span>"
            ),
        },
        domain={"x": [0, 1], "y": [0, 1]},
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color="#8888AA"),
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig