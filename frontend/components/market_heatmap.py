"""
Market heatmap — demand/supply/momentum visual grid.
"""
import plotly.graph_objects as go


def render_market_heatmap(comparisons: list) -> go.Figure:
    """
    Renders a heatmap comparing multiple neighborhoods across key metrics.
    comparisons: list of dicts from the /analyze/compare endpoint.
    """
    if not comparisons:
        return go.Figure()

    metrics = [
        "Median Price ($M)",
        "1Y Change (%)",
        "Days on Market",
        "Rental Yield (%)",
        "Walk Score",
        "Confidence Score",
    ]

    neighborhoods = [f"{c.get('neighborhood','')}" for c in comparisons]

    def extract_row(comp):
        raw   = comp.get("raw_data", {})
        score = comp.get("confidence_score", {})
        return [
            raw.get("median_price", 0) / 1_000_000,
            raw.get("price_change_1y", 0),
            raw.get("avg_days_on_market", 0),
            raw.get("rental_yield", 0),
            raw.get("walk_score", 0),
            score.get("overall", 0),
        ]

    z_raw  = [extract_row(c) for c in comparisons]
    z_text = []
    for row in z_raw:
        z_text.append([
            f"${row[0]:.2f}M",
            f"{row[1]:+.1f}%",
            f"{row[2]:.0f}d",
            f"{row[3]:.1f}%",
            f"{row[4]:.0f}",
            f"{row[5]:.0f}",
        ])

    # Normalize each column 0-1 for color
    z_norm = []
    for col_i in range(len(metrics)):
        col_vals = [row[col_i] for row in z_raw]
        mn, mx   = min(col_vals), max(col_vals)
        rng      = mx - mn if mx != mn else 1
        z_norm.append([(v - mn) / rng for v in col_vals])

    # Transpose: rows = metrics, cols = neighborhoods
    z_display = list(map(list, zip(*z_norm)))
    text_display = list(map(list, zip(*z_text)))

    fig = go.Figure(go.Heatmap(
        z=z_display,
        x=neighborhoods,
        y=metrics,
        text=text_display,
        texttemplate="%{text}",
        textfont={"family": "DM Mono, monospace", "size": 12, "color": "#F0F0F8"},
        colorscale=[
            [0.0,  "#1a1a2e"],
            [0.5,  "#1d4a3e"],
            [1.0,  "#00C896"],
        ],
        showscale=False,
        hovertemplate="<b>%{x}</b><br>%{y}: %{text}<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color="#8888AA", size=11),
        height=300,
        margin=dict(l=130, r=20, t=30, b=60),
        xaxis=dict(side="bottom", tickangle=-20),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def render_demand_supply_matrix(signals_list: list, labels: list) -> go.Figure:
    """
    Scatter plot: demand score (x) vs supply tightness (y).
    Each point = one neighborhood.
    """
    x = [s.get("demand_score", 50) for s in signals_list]
    y = [s.get("supply_score", 50) for s in signals_list]
    sizes = [s.get("liquidity_score", 50) * 0.4 + 8 for s in signals_list]
    colors = ["#00C896", "#3B82F6", "#8B5CF6", "#F59E0B", "#F87171"]

    fig = go.Figure()
    for i, (xi, yi, label) in enumerate(zip(x, y, labels)):
        fig.add_trace(go.Scatter(
            x=[xi], y=[yi],
            mode="markers+text",
            name=label,
            text=[label],
            textposition="top center",
            textfont=dict(family="DM Mono, monospace", size=10, color="#8888AA"),
            marker=dict(
                size=sizes[i],
                color=colors[i % len(colors)],
                opacity=0.85,
                line=dict(color="#09090f", width=2),
            ),
            hovertemplate=f"<b>{label}</b><br>Demand: {xi:.0f}<br>Supply Tightness: {yi:.0f}<extra></extra>",
        ))

    fig.add_hline(y=50, line=dict(color="#1e1e30", width=1, dash="dot"))
    fig.add_vline(x=50, line=dict(color="#1e1e30", width=1, dash="dot"))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color="#8888AA", size=11),
        height=300,
        showlegend=False,
        margin=dict(l=40, r=20, t=36, b=40),
        title=dict(
            text="<span style='font-family:DM Mono;font-size:11px;letter-spacing:2px;color:#44445A'>DEMAND vs SUPPLY MATRIX</span>",
            font=dict(size=11), x=0,
        ),
        xaxis=dict(title="Demand Score", range=[0, 105], gridcolor="#1e1e30", zerolinecolor="#1e1e30"),
        yaxis=dict(title="Supply Tightness", range=[0, 105], gridcolor="#1e1e30", zerolinecolor="#1e1e30"),
    )
    return fig