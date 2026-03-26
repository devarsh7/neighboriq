"""
02_compare.py — Side-by-side neighborhood comparison page.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="NeighborIQ — Compare", page_icon="⚖️", layout="wide", initial_sidebar_state="collapsed")

css_path = Path(__file__).parent.parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from frontend.components.api_client import compare
from frontend.components.ui_helpers import nav_bar, section_header, compare_winner_badge
from frontend.components.charts import make_breakdown_bar
from frontend.components.market_heatmap import render_market_heatmap, render_demand_supply_matrix

st.markdown(nav_bar(), unsafe_allow_html=True)
st.markdown(section_header("COMPARE NEIGHBORHOODS"), unsafe_allow_html=True)

st.markdown("""
<div style="font-family:DM Mono,monospace;font-size:12px;color:#8888AA;margin-bottom:20px">
Analyze up to 3 neighborhoods side-by-side and find your top pick.
</div>
""", unsafe_allow_html=True)

cc1, cc2, cc3 = st.columns(3)
inputs = []
defaults = [("Leslieville","Toronto"), ("Liberty Village","Toronto"), ("Wynwood","Miami")]
labels   = ["Neighborhood A", "Neighborhood B", "Neighborhood C"]

for col, label, (dn, dc) in zip([cc1, cc2, cc3], labels, defaults):
    with col:
        st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:#8888AA;letter-spacing:1px;margin-bottom:8px">{label}</div>', unsafe_allow_html=True)
        n = st.text_input("Neighborhood", value=dn, key=f"cn_{label}", label_visibility="collapsed")
        c = st.text_input("City",         value=dc, key=f"cc_{label}", label_visibility="collapsed")
        inputs.append({"neighborhood": n, "city": c})

if st.button("Compare All →", key="compare_btn"):
    with st.spinner("Analyzing all neighborhoods..."):
        result = compare(inputs)
        st.session_state["compare_results"] = result

comp_data = st.session_state.get("compare_results")
if not comp_data:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#44445A">
      <div style="font-size:48px;margin-bottom:16px">⚖️</div>
      <div style="font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#8888AA">
        Enter neighborhoods above and hit Compare
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    comparisons = [c for c in comp_data.get("comparisons", []) if "error" not in c]
    if not comparisons:
        st.error("No valid results returned.")
    else:
        top_score = max(c["confidence_score"]["overall"] for c in comparisons)

        # Score cards
        score_cols = st.columns(len(comparisons))
        for col, comp in zip(score_cols, comparisons):
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

        # Heatmap
        st.markdown(section_header("METRIC HEATMAP"), unsafe_allow_html=True)
        fig_heat = render_market_heatmap(comparisons)
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

        # Demand/supply matrix
        signals_list = [c.get("market_signals", {}) for c in comparisons]
        nb_labels    = [c.get("neighborhood", "") for c in comparisons]
        fig_matrix   = render_demand_supply_matrix(signals_list, nb_labels)
        st.plotly_chart(fig_matrix, use_container_width=True, config={"displayModeBar": False})

        # Breakdown charts
        st.markdown(section_header("SCORE BREAKDOWN"), unsafe_allow_html=True)
        chart_cols = st.columns(len(comparisons))
        for col, comp in zip(chart_cols, comparisons):
            with col:
                fig = make_breakdown_bar(comp["confidence_score"].get("breakdown", {}))
                fig.update_layout(title=dict(
                    text=f"<span style='font-family:DM Mono;font-size:10px;color:#44445A'>{comp.get('neighborhood','').upper()}</span>",
                    x=0,
                ))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Key bullets
        st.markdown(section_header("KEY INSIGHTS"), unsafe_allow_html=True)
        bullet_cols = st.columns(len(comparisons))
        for col, comp in zip(bullet_cols, comparisons):
            with col:
                st.markdown(f'<div style="font-family:Syne,sans-serif;font-size:14px;font-weight:700;margin-bottom:8px">{comp.get("neighborhood","")}</div>', unsafe_allow_html=True)
                for b in comp.get("report_bullets", []):
                    st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:11px;color:#8888AA;padding:4px 0;border-left:2px solid #1e1e30;padding-left:10px;margin:3px 0">{b}</div>', unsafe_allow_html=True)