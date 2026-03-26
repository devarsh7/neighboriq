"""
Price trend chart component — 3-year simulated price history.
"""
import plotly.graph_objects as go
import numpy as np


def render_trend_chart(raw_data: dict) -> go.Figure:
    """
    Returns a Plotly line chart showing simulated 3-year price trend.
    Usage:
        fig = render_trend_chart(raw_data)
        st.plotly_chart(fig, use_container_width=True)
    """
    current  = raw_data.get("median_price", 1_000_000)
    p1y      = raw_data.get("price_change_1y", 3)
    p3y      = raw_data.get("price_change_3y", 12)
    nb_name  = raw_data.get("neighborhood", "")

    price_3y_ago = current / (1 + p3y / 100)

    quarters = [
        "Q1 '22","Q2 '22","Q3 '22","Q4 '22",
        "Q1 '23","Q2 '23","Q3 '23","Q4 '23",
        "Q1 '24","Q2 '24","Q3 '24","Q4 '24","Now",
    ]

    np.random.seed(abs(hash(nb_name)) % 9999)
    prices = list(np.linspace(price_3y_ago, current, 13))
    noise  = np.random.normal(0, current * 0.008, 13)
    prices = [max(p + n, 0) for p, n in zip(prices, noise)]

    fig = go.Figure()

    # Gradient fill
    fig.add_trace(go.Scatter(
        x=quarters, y=prices,
        fill="tozeroy",
        fillcolor="rgba(0,200,150,0.04)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Main line
    fig.add_trace(go.Scatter(
        x=quarters, y=prices,
        mode="lines+markers",
        line=dict(color="#00C896", width=2.5, shape="spline"),
        marker=dict(size=5, color="#00C896"),
        name="Median Price",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color="#8888AA", size=11),
        height=200,
        showlegend=False,
        margin=dict(l=10, r=10, t=36, b=10),
        title=dict(
            text="<span style='font-family:DM Mono;font-size:11px;letter-spacing:2px;color:#44445A'>PRICE TREND (3Y)</span>",
            font=dict(size=11), x=0,
        ),
        yaxis=dict(tickformat="$,.0f", gridcolor="#1e1e30", zerolinecolor="#1e1e30"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickangle=-30),
    )
    return fig