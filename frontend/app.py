import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="NeighborIQ — Real Estate Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

css_path = Path(__file__).parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.api_client import analyze, chat, compare, health_check
from frontend.components.ui_helpers import (
    nav_bar, metric_card, signal_bar,
    chips, section_header, report_card, chat_message,
    processing_steps, empty_state, compare_winner_badge,
)
from frontend.components.charts import (
    make_score_gauge, make_price_trend_chart,
    make_breakdown_bar, make_radar_chart,
)

# ── Session state init ─────────────────────────────────────────────────────
for key in ["result", "chat_history", "compare_results", "pending_nb", "pending_city"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["chat_history"] else []

# ── Nav ────────────────────────────────────────────────────────────────────
st.markdown(nav_bar(), unsafe_allow_html=True)

# ── Backend status ─────────────────────────────────────────────────────────
if not health_check():
    st.markdown("""
    <div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);
                border-radius:10px;padding:12px 18px;margin-bottom:20px;
                font-family:DM Mono,monospace;font-size:12px;color:#F87171">
    ⚠️  Backend offline — run:
    <code style="color:#FB923C">uvicorn backend.main:app --reload --port 8000</code>
    from the <code style="color:#FB923C">neighboriq/</code> directory
    </div>
    """, unsafe_allow_html=True)

tab_analyze, tab_compare, tab_about = st.tabs(["  ANALYZE  ", "  COMPARE  ", "  ABOUT  "])


# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — ANALYZE
# ══════════════════════════════════════════════════════════════════════════
with tab_analyze:

    # ── Quick picks — set pending state BEFORE widgets render ─────────
    st.markdown("""
    <div style="margin-bottom:6px">
    <span style="font-family:DM Mono,monospace;font-size:10px;color:#44445A;
                 letter-spacing:1px">QUICK PICKS</span>
    </div>
    """, unsafe_allow_html=True)

    quick_picks = [
        ("Leslieville",    "Toronto"),
        ("Liberty Village","Toronto"),
        ("The Annex",      "Toronto"),
        ("Wynwood",        "Miami"),
        ("Brooklyn",       "New York"),
        ("Queen West",     "Toronto"),
    ]

    qcols = st.columns(6)
    run_quick = False
    for i, (qn, qc) in enumerate(quick_picks):
        with qcols[i]:
            if st.button(qn, key=f"qp_{i}", help=f"{qn}, {qc}"):
                st.session_state["pending_nb"]   = qn
                st.session_state["pending_city"] = qc
                run_quick = True

    # ── Search inputs — use pending values as defaults if set ─────────
    col_n, col_c, col_btn = st.columns([3, 2, 1.2])
    with col_n:
        neighborhood = st.text_input(
            "Neighborhood",
            value=st.session_state.get("pending_nb") or "",
            placeholder="e.g. Leslieville, Liberty Village, Wynwood",
            label_visibility="collapsed",
        )
    with col_c:
        city = st.text_input(
            "City",
            value=st.session_state.get("pending_city") or "",
            placeholder="e.g. Toronto, Miami, New York",
            label_visibility="collapsed",
        )
    with col_btn:
        analyze_clicked = st.button("Analyze →", key="analyze_btn")

    # Clear pending after rendering
    st.session_state["pending_nb"]   = None
    st.session_state["pending_city"] = None

    st.markdown("---")

    # ── Run analysis ───────────────────────────────────────────────────
    if (analyze_clicked or run_quick) and neighborhood:
        with st.spinner("Running AI pipeline..."):
            result = analyze(neighborhood, city)
            if result:
                st.session_state["result"]       = result
                st.session_state["chat_history"] = []
                st.rerun()

    # ── Display results ────────────────────────────────────────────────
    result = st.session_state.get("result")

    if not result:
        st.markdown(empty_state(), unsafe_allow_html=True)
    else:
        raw     = result.get("raw_data", {})
        signals = result.get("market_signals", {})
        score   = result.get("confidence_score", {})
        report  = result.get("report", "")
        steps   = result.get("processing_steps", [])
        score_v = score.get("overall", 0)
        tier    = score.get("tier", "Hold")
        color   = score.get("tier_color", "#FACC15")

        st.markdown(f"""
        <div style="display:flex;align-items:baseline;gap:14px;margin:8px 0 24px 0">
          <div style="font-family:Syne,sans-serif;font-size:32px;font-weight:800;
                      letter-spacing:-1px;color:#F0F0F8">{raw.get('neighborhood','')}</div>
          <div style="font-family:DM Mono,monospace;font-size:14px;color:#8888AA">{raw.get('city','')}</div>
        </div>
        """, unsafe_allow_html=True)

        left, mid, right = st.columns([1.1, 1.6, 1.3])

        with left:
            st.plotly_chart(make_score_gauge(score_v, tier, color),
                            width="stretch", config={"displayModeBar": False})
            st.plotly_chart(make_breakdown_bar(score.get("breakdown", {})),
                            width="stretch", config={"displayModeBar": False})

        with mid:
            p1y  = raw.get("price_change_1y", 0)
            p3y  = raw.get("price_change_3y", 0)
            dom  = raw.get("avg_days_on_market", 0)
            rent = raw.get("rental_yield", 0)
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(metric_card(f"${raw.get('median_price',0)/1e6:.2f}M", "MEDIAN PRICE",  f"{p1y:+.1f}% YoY", p1y >= 0), unsafe_allow_html=True)
                st.markdown(metric_card(f"{dom}d", "DAYS ON MARKET", "fast" if dom < 12 else "moderate", dom < 20), unsafe_allow_html=True)
            with m2:
                st.markdown(metric_card(f"{rent:.1f}%", "RENTAL YIELD",  "strong" if rent > 5 else "avg", rent > 4.5), unsafe_allow_html=True)
                st.markdown(metric_card(f"${raw.get('price_per_sqft',0):,.0f}", "PRICE / SQFT", f"{p3y:+.1f}% (3Y)", p3y >= 0), unsafe_allow_html=True)
            st.plotly_chart(make_price_trend_chart(raw),
                            width="stretch", config={"displayModeBar": False})

        with right:
            st.plotly_chart(make_radar_chart(signals),
                            width="stretch", config={"displayModeBar": False})
            st.markdown(signal_bar("Walk Score",      raw.get("walk_score",0),          "#3B82F6"), unsafe_allow_html=True)
            st.markdown(signal_bar("Transit Score",   raw.get("transit_score",0),        "#8B5CF6"), unsafe_allow_html=True)
            st.markdown(signal_bar("Demand",          signals.get("demand_score",0),     "#00C896"), unsafe_allow_html=True)
            st.markdown(signal_bar("Supply Tightness",signals.get("supply_score",0),     "#F59E0B"), unsafe_allow_html=True)

        st.markdown(section_header("MARKET SIGNALS"), unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            st.markdown("**✅ Positive Signals**")
            st.markdown(chips(signals.get("positive_signals",[]), "chip-positive"), unsafe_allow_html=True)
        with s2:
            st.markdown("**⚠️ Risk Flags**")
            st.markdown(chips(signals.get("risk_flags",[]), "chip-risk"), unsafe_allow_html=True)

        st.markdown(section_header("AI INTELLIGENCE REPORT"), unsafe_allow_html=True)
        st.markdown(report_card(report), unsafe_allow_html=True)

        with st.expander("🔬 Analysis Pipeline Trace", expanded=False):
            st.markdown(processing_steps(steps), unsafe_allow_html=True)

        # ── Q&A Chat ───────────────────────────────────────────────────
        st.markdown(section_header("ASK THE ANALYST"), unsafe_allow_html=True)
        chat_history = st.session_state.get("chat_history", [])

        st.markdown("""
        <div style="margin-bottom:8px;font-family:DM Mono,monospace;
                    font-size:10px;color:#44445A;letter-spacing:1px">SUGGESTED QUESTIONS</div>
        """, unsafe_allow_html=True)

        quick_qs = [
            "Is this good for first-time buyers?",
            "What are the biggest risks?",
            "Compare to the city average",
            "Best sub-areas to target?",
        ]
        qcols2 = st.columns(4)
        for i, q in enumerate(quick_qs):
            with qcols2[i]:
                if st.button(q, key=f"qq_{i}"):
                    st.session_state["pending_question"] = q

        if chat_history:
            chat_html = '<div class="chat-container">'
            for msg in chat_history:
                chat_html += chat_message(msg["content"], msg["role"])
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)

        with st.form(key="chat_form", clear_on_submit=True):
            user_q = st.text_input(
                "Ask anything",
                value=st.session_state.pop("pending_question", ""),
                placeholder="e.g. Is this a good market for investors?",
                label_visibility="collapsed",
            )
            send = st.form_submit_button("Ask →")

        if send and user_q and result:
            with st.spinner("Thinking..."):
                resp = chat(user_q, result, chat_history)
                st.session_state["chat_history"] = resp.get("chat_history", [])
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE
# ══════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown(section_header("COMPARE NEIGHBORHOODS"), unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:DM Mono,monospace;font-size:12px;color:#8888AA;margin-bottom:20px">
    Analyze up to 3 neighborhoods side-by-side. AI scores each independently.
    </div>
    """, unsafe_allow_html=True)

    cc1, cc2, cc3 = st.columns(3)
    compare_inputs = []
    for i, (col, label, defaults) in enumerate(zip(
        [cc1, cc2, cc3],
        ["Neighborhood A", "Neighborhood B", "Neighborhood C"],
        [("Leslieville","Toronto"), ("Liberty Village","Toronto"), ("Wynwood","Miami")],
    )):
        with col:
            st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:#8888AA;letter-spacing:1px;margin-bottom:8px">{label}</div>', unsafe_allow_html=True)
            cn = st.text_input("Neighborhood", value=defaults[0], key=f"cn_{i}", label_visibility="collapsed")
            cc = st.text_input("City",         value=defaults[1], key=f"cc_{i}", label_visibility="collapsed")
            compare_inputs.append({"neighborhood": cn, "city": cc})

    if st.button("Compare All →", key="compare_btn"):
        with st.spinner("Running parallel analysis..."):
            comp_result = compare(compare_inputs)
            st.session_state["compare_results"] = comp_result

    comp_data = st.session_state.get("compare_results")
    if comp_data and comp_data.get("comparisons"):
        valid     = [c for c in comp_data["comparisons"] if "error" not in c]
        top_score = max(c["confidence_score"]["overall"] for c in valid) if valid else 0

        score_cols = st.columns(len(valid))
        for col, comp in zip(score_cols, valid):
            s         = comp["confidence_score"]
            is_winner = s["overall"] == top_score
            badge     = compare_winner_badge(is_winner)
            with col:
                st.markdown(f"""
                <div style="background:#13131f;border:1px solid {'#00C896' if is_winner else '#1e1e30'};
                            border-radius:16px;padding:24px;text-align:center;margin-bottom:16px">
                  <div style="font-family:Syne,sans-serif;font-size:16px;font-weight:700">
                    {comp.get('neighborhood','')}{badge}
                  </div>
                  <div style="font-family:DM Mono,monospace;font-size:11px;color:#8888AA">{comp.get('city','')}</div>
                  <div style="font-family:Syne,sans-serif;font-size:52px;font-weight:800;
                              color:{s['tier_color']};line-height:1.1;margin:12px 0">{s['overall']:.0f}</div>
                  <div style="font-family:DM Mono,monospace;font-size:11px;
                              color:{s['tier_color']};letter-spacing:2px">{s['tier'].upper()}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(section_header("SIDE-BY-SIDE METRICS"), unsafe_allow_html=True)
        metrics_rows = [
            ("Median Price",   lambda r: f"${r.get('median_price',0)/1e6:.2f}M"),
            ("1Y Change",      lambda r: f"{r.get('price_change_1y',0):+.1f}%"),
            ("3Y Change",      lambda r: f"{r.get('price_change_3y',0):+.1f}%"),
            ("Days on Market", lambda r: f"{r.get('avg_days_on_market',0)}d"),
            ("Rental Yield",   lambda r: f"{r.get('rental_yield',0):.1f}%"),
            ("Price/sqft",     lambda r: f"${r.get('price_per_sqft',0):,.0f}"),
            ("Walk Score",     lambda r: str(r.get("walk_score",0))),
        ]
        table_html = '<table class="compare-table"><thead><tr><th>METRIC</th>'
        for comp in valid:
            table_html += f"<th>{comp.get('neighborhood','').upper()}</th>"
        table_html += "</tr></thead><tbody>"
        for label, fn in metrics_rows:
            table_html += f"<tr><td style='font-family:DM Mono,monospace;font-size:11px;color:#44445A;letter-spacing:1px'>{label}</td>"
            for comp in valid:
                table_html += f"<td>{fn(comp.get('raw_data',{}))}</td>"
            table_html += "</tr>"
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

        st.markdown(section_header("SCORE BREAKDOWN"), unsafe_allow_html=True)
        chart_cols = st.columns(len(valid))
        for col, comp in zip(chart_cols, valid):
            with col:
                fig = make_breakdown_bar(comp["confidence_score"].get("breakdown", {}))
                fig.update_layout(title=dict(
                    text=f"<span style='font-family:DM Mono;font-size:10px;color:#44445A;letter-spacing:1px'>{comp.get('neighborhood','').upper()}</span>",
                    x=0,
                ))
                st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — ABOUT
# ══════════════════════════════════════════════════════════════════════════
with tab_about:
    st.markdown(section_header("ABOUT NEIGHBORIQ"), unsafe_allow_html=True)
    st.markdown("""
    <div class="report-card">
    <p><strong style="color:#F0F0F8">NeighborIQ</strong> is an AI-native real estate intelligence
    platform that compresses hours of market research into seconds using a multi-agent pipeline.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(section_header("ARCHITECTURE"), unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1:
        st.markdown("""
        <div class="report-card" style="font-family:DM Mono,monospace;font-size:12px;line-height:1.9">
        <div style="color:#00C896;letter-spacing:2px;margin-bottom:12px">AGENT PIPELINE</div>
        Node 1 → Data Fetcher<br>
        Node 2 → Market Analyzer<br>
        Node 3 → Confidence Scorer<br>
        Node 4 → Claude Report Generator<br>
        Node 5 → Conversational Q&A Agent<br>
        <br>
        <div style="color:#8888AA">Orchestrated via LangGraph StateGraph</div>
        </div>
        """, unsafe_allow_html=True)
    with a2:
        st.markdown("""
        <div class="report-card" style="font-family:DM Mono,monospace;font-size:12px;line-height:1.9">
        <div style="color:#3B82F6;letter-spacing:2px;margin-bottom:12px">TECH STACK</div>
        LLM → Claude Sonnet (Anthropic)<br>
        Orchestration → LangGraph + LangChain<br>
        Backend → FastAPI (async)<br>
        Frontend → Streamlit<br>
        Search → Brave MCP Server<br>
        <br>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(section_header("PRELOADED NEIGHBORHOODS"), unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:DM Mono,monospace;font-size:12px;color:#8888AA;
                display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
    <span>The Annex · Toronto</span><span>Leslieville · Toronto</span>
    <span>Liberty Village · Toronto</span><span>Queen West · Toronto</span>
    <span>Scarborough · Toronto</span><span>Brooklyn · New York</span>
    <span>Wynwood · Miami</span><span>Mission District · SF</span>
    </div>
    """, unsafe_allow_html=True)