"""
Market signal cards component.
Renders positive signals and risk flags as styled HTML chips.
"""


def render_signal_bar(label: str, value: float, color: str = "#00C896") -> str:
    """Single horizontal signal bar with label and value."""
    return f"""
    <div style="margin:8px 0">
      <div style="display:flex;justify-content:space-between;
                  font-family:DM Mono,monospace;font-size:11px;
                  color:#8888AA;margin-bottom:5px">
        <span>{label}</span>
        <span style="color:{color}">{value:.0f}</span>
      </div>
      <div style="height:6px;background:#0f0f1a;border-radius:3px;overflow:hidden">
        <div style="width:{value}%;height:100%;background:{color};border-radius:3px"></div>
      </div>
    </div>
    """


def render_chips(items: list, chip_type: str = "positive") -> str:
    """
    Render a list of signal items as colored chips.
    chip_type: "positive" | "risk"
    """
    if not items:
        return '<div style="color:#44445A;font-family:DM Mono;font-size:11px">None identified</div>'

    if chip_type == "positive":
        bg    = "rgba(0,200,150,0.1)"
        border = "rgba(0,200,150,0.3)"
        color  = "#00C896"
    else:
        bg    = "rgba(248,113,113,0.1)"
        border = "rgba(248,113,113,0.3)"
        color  = "#F87171"

    html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0">'
    for item in items:
        html += (
            f'<span style="font-family:DM Mono,monospace;font-size:11px;'
            f'padding:4px 10px;border-radius:20px;line-height:1.5;'
            f'background:{bg};border:1px solid {border};color:{color}">'
            f'{item}</span>'
        )
    html += "</div>"
    return html


def render_metric_card(value: str, label: str, delta: str = "", positive: bool = True) -> str:
    """Individual metric card with value, label and optional delta."""
    delta_color = "#00C896" if positive else "#F87171"
    delta_html  = (
        f'<div style="font-family:DM Mono,monospace;font-size:11px;'
        f'color:{delta_color};margin-top:2px">{delta}</div>'
    ) if delta else ""

    return f"""
    <div style="background:#0f0f1a;border:1px solid #1e1e30;
                border-radius:12px;padding:16px">
      <div style="font-family:Syne,sans-serif;font-size:22px;
                  font-weight:700;color:#F0F0F8;line-height:1.1">{value}</div>
      <div style="font-family:DM Mono,monospace;font-size:10px;
                  color:#44445A;letter-spacing:1.5px;
                  text-transform:uppercase;margin-top:4px">{label}</div>
      {delta_html}
    </div>
    """


def render_score_pill(score: float, tier: str, color: str) -> str:
    """Compact score pill for use in lists/tables."""
    return (
        f'<span style="font-family:Syne,sans-serif;font-size:18px;'
        f'font-weight:700;color:{color}">{score:.0f}</span>'
        f'<span style="font-family:DM Mono,monospace;font-size:10px;'
        f'color:{color};letter-spacing:2px;margin-left:6px">{tier.upper()}</span>'
    )