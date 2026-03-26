def nav_bar() -> str:
    return """
    <div class="neighboriq-nav">
      <div class="neighboriq-logo">Neighbor<span>IQ</span></div>
      <div style="display:flex;align-items:center;gap:12px">
        <span class="live-dot"></span>
        <span class="nav-badge">AI INTELLIGENCE</span>
      </div>
    </div>
    """


def score_display(score: float, tier: str, color: str) -> str:
    return f"""
    <div style="text-align:center;padding:16px 0">
      <div class="score-label">CONFIDENCE SCORE</div>
      <div class="score-number" style="color:{color}">{score:.0f}</div>
      <div style="font-family:'DM Mono',monospace;font-size:11px;color:{color};
                  letter-spacing:3px;opacity:0.85;margin-top:6px">{tier.upper()}</div>
    </div>
    """


def metric_card(value: str, label: str, delta: str = "", positive: bool = True) -> str:
    delta_class = "delta-pos" if positive else "delta-neg"
    delta_html = f'<div class="metric-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
      <div class="metric-value">{value}</div>
      <div class="metric-label">{label}</div>
      {delta_html}
    </div>
    """


def signal_bar(label: str, value: float, color: str = "#00C896") -> str:
    return f"""
    <div class="signal-bar-container">
      <div class="signal-bar-label">
        <span>{label}</span>
        <span style="color:{color}">{value:.0f}</span>
      </div>
      <div class="signal-bar-track">
        <div class="signal-bar-fill" style="width:{value}%;background:{color}"></div>
      </div>
    </div>
    """


def chips(items: list, chip_class: str) -> str:
    if not items:
        return '<div style="color:#44445A;font-family:DM Mono;font-size:11px">None identified</div>'
    html = '<div class="chip-container">'
    for item in items:
        html += f'<span class="chip {chip_class}">{item}</span>'
    html += "</div>"
    return html


def section_header(title: str) -> str:
    return f'<div class="section-header">{title}</div>'


def report_card(text: str) -> str:
    paragraphs = [f"<p>{p.strip()}</p>" for p in text.split("\n\n") if p.strip()]
    return f'<div class="report-card">{"".join(paragraphs)}</div>'


def chat_message(content: str, role: str) -> str:
    if role == "user":
        return f"""
        <div class="chat-msg-user">
          <div class="chat-sender chat-sender-user">YOU</div>
          {content}
        </div>"""
    else:
        return f"""
        <div class="chat-msg-ai">
          <div class="chat-sender chat-sender-ai">NEIGHBORIQ</div>
          {content}
        </div>"""


def processing_steps(steps: list) -> str:
    html = '<div style="padding:12px 0">'
    for step in steps:
        html += f'<div class="step-item done">{step}</div>'
    html += "</div>"
    return html


def empty_state() -> str:
    return """
    <div style="text-align:center;padding:60px 20px;color:#44445A">
      <div style="font-size:48px;margin-bottom:16px">🏙️</div>
      <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;
                  color:#8888AA;margin-bottom:8px">Enter a neighborhood to begin</div>
      <div style="font-family:DM Mono,monospace;font-size:12px;letter-spacing:1px">
        Try: Leslieville, Toronto · Liberty Village · Wynwood, Miami
      </div>
    </div>
    """


def compare_winner_badge(is_winner: bool) -> str:
    if not is_winner:
        return ""
    return """<span style="font-family:DM Mono,monospace;font-size:10px;
               background:rgba(0,200,150,0.15);color:#00C896;
               border:1px solid rgba(0,200,150,0.3);border-radius:20px;
               padding:2px 8px;margin-left:8px;letter-spacing:1px">TOP PICK</span>"""