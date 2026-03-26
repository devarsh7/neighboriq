"""
03_reports.py — Saved reports browser page.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="NeighborIQ — Reports", page_icon="📁", layout="wide", initial_sidebar_state="collapsed")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.ui_helpers import nav_bar, section_header, report_card
from frontend.components.score_gauge import render_score_gauge
from backend.services.report_service import list_reports, get_report, delete_report, save_analysis

st.markdown(nav_bar(), unsafe_allow_html=True)
st.markdown(section_header("SAVED REPORTS"), unsafe_allow_html=True)

# Save current analysis if exists
if st.session_state.get("result"):
    if st.button("💾 Save Current Analysis"):
        path = save_analysis(st.session_state["result"])
        st.success(f"Saved: {Path(path).name}")

reports = list_reports()

if not reports:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#44445A">
      <div style="font-size:48px;margin-bottom:16px">📁</div>
      <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#8888AA;margin-bottom:8px">
        No saved reports yet
      </div>
      <div style="font-family:DM Mono,monospace;font-size:12px;letter-spacing:1px">
        Run an analysis and click Save to store it here
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="font-family:DM Mono,monospace;font-size:11px;color:#44445A;
                letter-spacing:1px;margin-bottom:16px">
    {len(reports)} REPORT{"S" if len(reports) != 1 else ""} SAVED
    </div>
    """, unsafe_allow_html=True)

    for report_meta in reports:
        score = report_meta.get("score", 0)
        tier  = report_meta.get("tier", "")
        color_map = {
            "Strong Buy": "#00C896", "Buy": "#4ADE80",
            "Hold": "#FACC15", "Caution": "#FB923C", "Avoid": "#F87171",
        }
        color = color_map.get(tier, "#FACC15")

        with st.expander(
            f"🏙️  {report_meta['neighborhood']}, {report_meta['city']}  —  "
            f"Score: {score:.0f} ({tier})  —  {report_meta['saved_at'][:10]}"
        ):
            full = get_report(report_meta["filepath"])
            if full:
                col_gauge, col_report = st.columns([1, 2.5])
                with col_gauge:
                    fig = render_score_gauge(score, tier, color)
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                    raw = full.get("raw_data", {})
                    st.markdown(f"""
                    <div style="font-family:DM Mono,monospace;font-size:11px;color:#8888AA;line-height:1.9">
                    Median: ${raw.get('median_price',0)/1e6:.2f}M<br>
                    1Y: {raw.get('price_change_1y',0):+.1f}%<br>
                    DOM: {raw.get('avg_days_on_market',0)}d<br>
                    Yield: {raw.get('rental_yield',0):.1f}%
                    </div>
                    """, unsafe_allow_html=True)
                with col_report:
                    st.markdown(report_card(full.get("report", "")), unsafe_allow_html=True)

                if st.button("🗑️ Delete", key=f"del_{report_meta['filepath']}"):
                    delete_report(report_meta["filepath"])
                    st.rerun()