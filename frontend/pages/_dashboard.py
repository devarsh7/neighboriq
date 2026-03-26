"""
01_dashboard.py — Main analysis dashboard page.
Streamlit multi-page app entry for the Analyze tab.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="NeighborIQ — Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

css_path = Path(__file__).parent.parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.api_client import analyze, health_check
from frontend.components.ui_helpers import (
    nav_bar, section_header, report_card,
    chips, processing_steps, empty_state,
)
from frontend.components.signal_cards import render_signal_bar, render_metric_card
from frontend.components.score_gauge import render_score_gauge
from frontend.components.trend_chart import render_trend_chart
from frontend.components.chat_interface import render_chat_input
from frontend.components.charts import make_breakdown_bar, make_radar_chart
from frontend.config import QUICK_PICKS

# Session state
for k in ["result", "chat_history"]:
    if k not in st.session_state:
        st.session_state[k] = None if k != "chat_history" else []

st.markdown(nav_bar(), unsafe_allow_html=True)

# Backend warning
if not health_check():
    st.markdown("""
    <div style="background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.25);
                border-radius:10px;padding:12px 18px;margin-bottom:20px;
                font-family:DM Mono,monospace;font-size:12px;color:#F87171">
    ⚠️ Backend offline — run:
    <code style="color:#FB923C">uvicorn backend.main:app --reload --port 8000</code>
    </div>
    """, unsafe_allow_html=True)

# Search
col_n, col_c, col_btn = st.columns([3, 2, 1.2])
with col_n:
    neighborhood = st.text_input("Neighborhood", placeholder="e.g. Leslieville", label_visibility="collapsed")
with col_c:
    city = st.text_input("City", placeholder="e.g. Toronto", label_visibility="collapsed")
with col_btn:
    go = st.button("Analyze →")

# Quick picks
qcols = st.columns(len(QUICK_PICKS))
for i, (qn, qc) in enumerate(QUICK_PICKS):
    with qcols[i]:
        if st.button(qn, key=f"qp_{i}"):
            neighborhood, city, go = qn, qc, True

st.markdown("---")

if go and neighborhood:
    with st.spinner("Running AI pipeline..."):
        result = analyze(neighborhood, city)
        if result:
            st.session_state["result"] = result
            st.session_state["chat_history"] = []

result = st.session_state.get("result")

if not result:
    st.markdown(empty_state(), unsafe_allow_html=True)
else:
    raw     = result.get("raw_data", {})
    signals = result.get("market_signals", {})
    score   = result.get("confidence_score", {})
    report  = result.get("report", "")
    steps   = result.get("processing_steps", [])

    st.markdown(f"""
    <div style="display:flex;align-items:baseline;gap:14px;margin:8px 0 24px">
      <div style="font-family:Syne,sans-serif;font-size:32px;font-weight:800;
                  letter-spacing:-1px;color:#F0F0F8">{raw.get('neighborhood','')}</div>
      <div style="font-family:DM Mono,monospace;font-size:14px;color:#8888AA">{raw.get('city','')}</div>
    </div>
    """, unsafe_allow_html=True)

    left, mid, right = st.columns([1.1, 1.6, 1.3])

    with left:
        fig = render_score_gauge(score.get("overall", 0), score.get("tier", ""), score.get("tier_color", "#FACC15"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        fig2 = make_breakdown_bar(score.get("breakdown", {}))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with mid:
        m1, m2 = st.columns(2)
        p1y = raw.get("price_change_1y", 0)
        with m1:
            st.markdown(render_metric_card(f"${raw.get('median_price',0)/1e6:.2f}M", "MEDIAN PRICE", f"{p1y:+.1f}% YoY", p1y >= 0), unsafe_allow_html=True)
            st.markdown(render_metric_card(f"{raw.get('avg_days_on_market',0)}d", "DAYS ON MARKET", "fast" if raw.get("avg_days_on_market", 20) < 14 else "moderate", raw.get("avg_days_on_market", 20) < 20), unsafe_allow_html=True)
        with m2:
            st.markdown(render_metric_card(f"{raw.get('rental_yield',0):.1f}%", "RENTAL YIELD", "strong" if raw.get("rental_yield",0) > 5 else "avg", raw.get("rental_yield",0) > 4.5), unsafe_allow_html=True)
            st.markdown(render_metric_card(f"${raw.get('price_per_sqft',0):,.0f}", "PRICE / SQFT", f"{raw.get('price_change_3y',0):+.1f}% (3Y)", raw.get("price_change_3y",0) >= 0), unsafe_allow_html=True)
        fig3 = render_trend_chart(raw)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with right:
        fig4 = make_radar_chart(signals)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        st.markdown(render_signal_bar("Walk Score",     raw.get("walk_score", 0),             "#3B82F6"), unsafe_allow_html=True)
        st.markdown(render_signal_bar("Transit Score",  raw.get("transit_score", 0),           "#8B5CF6"), unsafe_allow_html=True)
        st.markdown(render_signal_bar("Demand",         signals.get("demand_score", 0),        "#00C896"), unsafe_allow_html=True)
        st.markdown(render_signal_bar("Supply Tightness", signals.get("supply_score", 0),      "#F59E0B"), unsafe_allow_html=True)

    st.markdown(section_header("MARKET SIGNALS"), unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**✅ Positive Signals**")
        st.markdown(chips(signals.get("positive_signals", []), "chip-positive"), unsafe_allow_html=True)
    with c2:
        st.markdown("**⚠️ Risk Flags**")
        st.markdown(chips(signals.get("risk_flags", []), "chip-risk"), unsafe_allow_html=True)

    st.markdown(section_header("AI REPORT"), unsafe_allow_html=True)
    st.markdown(report_card(report), unsafe_allow_html=True)

    with st.expander("🔬 Pipeline Trace"):
        st.markdown(processing_steps(steps), unsafe_allow_html=True)

    st.markdown(section_header("ASK THE ANALYST"), unsafe_allow_html=True)
    render_chat_input(result, key_suffix="dashboard")