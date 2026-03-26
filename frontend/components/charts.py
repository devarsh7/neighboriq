import plotly.graph_objects as go
import numpy as np

COLORS = {
    "bg":         "#09090f",
    "bg_card":    "#13131f",
    "border":     "#1e1e30",
    "green":      "#00C896",
    "blue":       "#3B82F6",
    "purple":     "#8B5CF6",
    "amber":      "#F59E0B",
    "red":        "#F87171",
    "text":       "#F0F0F8",
    "text_muted": "#8888AA",
}

# Only truly shared keys — nothing that any chart overrides
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color=COLORS["text_muted"], size=11),
)

def _axis(gridcolor=None, tickformat=None, tickangle=None,
          range_=None, autorange=None, zerolinecolor=None):
    """Build an axis dict with only the keys we actually set."""
    d = dict(showline=False)
    d["gridcolor"]     = gridcolor or COLORS["border"]
    d["zerolinecolor"] = zerolinecolor or COLORS["border"]
    if tickformat  is not None: d["tickformat"]  = tickformat
    if tickangle   is not None: d["tickangle"]   = tickangle
    if range_      is not None: d["range"]       = range_
    if autorange   is not None: d["autorange"]   = autorange
    return d


def make_score_gauge(score: float, tier: str, color: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            "font": {"family": "Syne, sans-serif", "size": 52, "color": color},
            "suffix": "",
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickfont": {"family": "DM Mono, monospace", "size": 10, "color": COLORS["text_muted"]},
                "tickvals": [0, 25, 50, 75, 100],
                "ticktext": ["0", "25", "50", "75", "100"],
            },
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": COLORS["bg_card"],
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
                f"color:{COLORS['text_muted']};letter-spacing:2px'>{tier.upper()}</span>"
            ),
            "font": {"size": 12},
        },
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


def make_price_trend_chart(raw_data: dict) -> go.Figure:
    current      = raw_data.get("median_price", 1_000_000)
    p3y          = raw_data.get("price_change_3y", 12)
    price_3y_ago = current / (1 + p3y / 100)

    quarters = [
        "Q1 '22", "Q2 '22", "Q3 '22", "Q4 '22",
        "Q1 '23", "Q2 '23", "Q3 '23", "Q4 '23",
        "Q1 '24", "Q2 '24", "Q3 '24", "Q4 '24", "Now",
    ]

    np.random.seed(abs(hash(raw_data.get("neighborhood", ""))) % 999)
    prices = list(np.linspace(price_3y_ago, current, 13))
    noise  = np.random.normal(0, current * 0.01, 13)
    prices = [max(p + n, 0) for p, n in zip(prices, noise)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=quarters, y=prices,
        fill="tozeroy",
        fillcolor="rgba(0,200,150,0.04)",
        line=dict(color="rgba(0,200,150,0)", width=0),
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=quarters, y=prices,
        mode="lines+markers",
        line=dict(color=COLORS["green"], width=2.5, shape="spline"),
        marker=dict(size=5, color=COLORS["green"], symbol="circle"),
        name="Median Price",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        height=200,
        margin=dict(l=10, r=10, t=36, b=10),
        showlegend=False,
        title=dict(
            text="<span style='font-family:DM Mono;font-size:11px;letter-spacing:2px;color:#44445A'>PRICE TREND (3Y)</span>",
            font=dict(size=11),
            x=0,
        ),
        xaxis=_axis(gridcolor="rgba(0,0,0,0)", tickangle=-30),
        yaxis=_axis(tickformat="$,.0f"),
    )
    return fig


def make_breakdown_bar(breakdown: dict) -> go.Figure:
    labels       = list(breakdown.keys())
    values       = list(breakdown.values())
    max_possible = [25, 25, 15, 15, 10, 10]

    colors = []
    for v, mx in zip(values, max_possible):
        ratio = v / mx if mx else 0
        if ratio > 0.75:  colors.append(COLORS["green"])
        elif ratio > 0.5: colors.append(COLORS["blue"])
        elif ratio > 0.3: colors.append(COLORS["amber"])
        else:             colors.append(COLORS["red"])

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{y}</b>: %{x:.1f} pts<extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        height=220,
        margin=dict(l=10, r=10, t=36, b=10),
        title=dict(
            text="<span style='font-family:DM Mono;font-size:11px;letter-spacing:2px;color:#44445A'>SCORE BREAKDOWN</span>",
            font=dict(size=11),
            x=0,
        ),
        xaxis=_axis(range_=[0, 26]),
        yaxis=_axis(autorange="reversed"),
        bargap=0.35,
    )
    return fig


def make_radar_chart(signals: dict) -> go.Figure:
    categories     = ["Demand", "Supply\nTightness", "Liquidity", "Momentum", "Sentiment"]
    momentum_norm  = (signals.get("price_momentum", 0) + 1) * 50
    sentiment_norm = (signals.get("news_sentiment", 0) + 1) * 50

    values = [
        signals.get("demand_score", 50),
        signals.get("supply_score", 50),
        signals.get("liquidity_score", 50),
        momentum_norm,
        sentiment_norm,
    ]
    values_closed = values + [values[0]]
    cats_closed   = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_closed,
        theta=cats_closed,
        fill="toself",
        fillcolor="rgba(0,200,150,0.08)",
        line=dict(color=COLORS["green"], width=2),
        marker=dict(size=5, color=COLORS["green"]),
        hovertemplate="<b>%{theta}</b>: %{r:.0f}<extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        height=260,
        margin=dict(l=40, r=40, t=40, b=20),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=COLORS["border"],
                linecolor=COLORS["border"],
                tickfont=dict(size=9, color=COLORS["text_muted"]),
                tickvals=[25, 50, 75, 100],
            ),
            angularaxis=dict(
                gridcolor=COLORS["border"],
                linecolor=COLORS["border"],
                tickfont=dict(family="DM Mono, monospace", size=10, color=COLORS["text_muted"]),
            ),
        ),
        title=dict(
            text="<span style='font-family:DM Mono;font-size:11px;letter-spacing:2px;color:#44445A'>MARKET RADAR</span>",
            font=dict(size=11),
            x=0,
        ),
        showlegend=False,
    )
    return fig