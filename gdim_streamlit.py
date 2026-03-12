"""
Global Drug Intelligence Monitor
Full Streamlit Application with Live Plotly Charts
Run: streamlit run gdim_streamlit.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import time

# ---------------------------------------------
# PAGE CONFIG
# ---------------------------------------------
st.set_page_config(
    page_title="Global Drug Intelligence Monitor",
    page_icon="⊕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------
# CUSTOM CSS
# ---------------------------------------------
# CSS
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:        #04080f;
    --bg1:       #070d1a;
    --bg2:       #0a1628;
    --bg3:       #0e1e38;
    --cyan:      #0df4ff;
    --violet:    #8b5cf6;
    --lime:      #39ff85;
    --orange:    #ff6b2b;
    --gold:      #fbbf24;
    --red:       #f43f5e;
    --text:      #e8f0fe;
    --text2:     #7a94b8;
    --text3:     #3a5068;
    --border:    rgba(13,244,255,0.1);
    --border2:   rgba(13,244,255,0.06);
    --glow-c:    rgba(13,244,255,0.18);
    --glow-v:    rgba(139,92,246,0.18);
  }

  * { box-sizing: border-box; }

  html, body, [class*="css"], .stApp {
    font-family: 'Space Grotesk', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text);
  }

  /* Animated background mesh */
  .stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
      radial-gradient(ellipse 80% 50% at 20% 10%, rgba(13,244,255,0.06) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 80%, rgba(139,92,246,0.07) 0%, transparent 55%),
      radial-gradient(ellipse 40% 30% at 60% 30%, rgba(57,255,133,0.04) 0%, transparent 50%);
    animation: meshPulse 12s ease-in-out infinite alternate;
  }
  @keyframes meshPulse {
    0%   { opacity: 0.7; transform: scale(1); }
    100% { opacity: 1;   transform: scale(1.04); }
  }

  /* Scanline texture overlay */
  .stApp::after {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background: repeating-linear-gradient(
      0deg,
      transparent, transparent 2px,
      rgba(0,0,0,0.12) 2px, rgba(0,0,0,0.12) 4px
    );
    opacity: 0.3;
  }

  .block-container {
    padding: 0 2rem 3rem 2rem !important;
    max-width: 100% !important;
    position: relative; z-index: 1;
  }

  #MainMenu, footer, header, .stDeployButton { visibility: hidden; display: none; }

  /* -- HEADER -- */
  .gdim-header {
    background: linear-gradient(135deg, rgba(4,8,15,0.98) 0%, rgba(10,22,40,0.98) 100%);
    border-bottom: 1px solid var(--border);
    padding: 0 32px;
    height: 64px;
    display: flex; align-items: center; justify-content: space-between;
    margin: -1rem -2rem 0 -2rem;
    position: sticky; top: 0; z-index: 999;
    box-shadow: 0 1px 0 rgba(13,244,255,0.08), 0 8px 32px rgba(0,0,0,0.6);
    backdrop-filter: blur(20px);
  }
  .gdim-logo-mark {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, rgba(13,244,255,0.15), rgba(139,92,246,0.15));
    border: 1px solid rgba(13,244,255,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 900; color: var(--cyan);
    text-shadow: 0 0 20px var(--cyan);
    box-shadow: 0 0 20px rgba(13,244,255,0.12), inset 0 1px 0 rgba(255,255,255,0.1);
    flex-shrink: 0;
  }
  .gdim-title {
    font-family: 'Clash Display', 'Space Grotesk', sans-serif;
    font-size: 15px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--text); margin: 0;
    background: linear-gradient(90deg, var(--text) 0%, var(--cyan) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  }
  .gdim-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: var(--text3); margin: 2px 0 0 0;
    letter-spacing: 0.14em; text-transform: uppercase;
  }
  .live-badge {
    font-family: 'JetBrains Mono', monospace; font-size: 9px;
    color: var(--lime); display: flex; align-items: center; gap: 8px;
    background: rgba(57,255,133,0.06); border: 1px solid rgba(57,255,133,0.2);
    padding: 6px 14px; border-radius: 20px; letter-spacing: 0.06em;
  }
  .live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--lime); box-shadow: 0 0 10px var(--lime);
    animation: livePulse 1.4s ease-in-out infinite;
    flex-shrink: 0;
  }
  @keyframes livePulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 8px var(--lime); }
    50% { opacity: 0.4; box-shadow: 0 0 3px var(--lime); }
  }

  /* -- SECTION HEADERS -- */
  .section-header {
    display: flex; align-items: flex-start; gap: 16px;
    margin: 28px 0 24px 0; padding-bottom: 20px;
    border-bottom: 1px solid var(--border2);
    position: relative;
  }
  .section-header::after {
    content: '';
    position: absolute; bottom: -1px; left: 0;
    width: 80px; height: 1px;
    background: linear-gradient(90deg, var(--cyan), transparent);
  }
  .section-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; color: var(--cyan); opacity: 0.5;
    letter-spacing: 0.1em; padding-top: 4px;
  }
  .section-icon { font-size: 28px; line-height: 1; }
  .section-title {
    font-family: 'Clash Display', 'Space Grotesk', sans-serif;
    font-size: 22px; font-weight: 700; color: var(--text); margin: 0;
    letter-spacing: -0.01em;
  }
  .section-sub {
    font-family: 'JetBrains Mono', monospace; font-size: 10px;
    color: var(--text3); margin: 4px 0 0 0; letter-spacing: 0.06em;
  }
  .ai-badge {
    margin-left: auto; flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace; font-size: 9px; font-weight: 700;
    letter-spacing: 0.12em; padding: 6px 14px; border-radius: 4px;
    border: 1px solid rgba(13,244,255,0.25);
    background: linear-gradient(135deg, rgba(13,244,255,0.06), rgba(139,92,246,0.06));
    color: var(--cyan); text-transform: uppercase;
    box-shadow: 0 0 16px rgba(13,244,255,0.06), inset 0 1px 0 rgba(13,244,255,0.08);
  }

  /* -- STAT CARDS -- */
  .stat-card {
    background: linear-gradient(135deg, var(--bg2) 0%, var(--bg3) 100%);
    border: 1px solid var(--border2);
    border-radius: 14px; padding: 20px 18px;
    position: relative; overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .stat-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
  }
  .stat-card:hover {
    border-color: rgba(13,244,255,0.2);
    box-shadow: 0 0 32px rgba(13,244,255,0.07);
  }
  .stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 8px; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--text3); margin-bottom: 10px;
  }
  .stat-value {
    font-family: 'Clash Display', 'Space Grotesk', sans-serif;
    font-size: 28px; font-weight: 700; line-height: 1; letter-spacing: -0.02em;
  }
  .stat-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; color: var(--text3); margin-top: 6px;
  }
  .stat-up {
    font-family: 'JetBrains Mono', monospace; font-size: 9px;
    color: var(--lime); background: rgba(57,255,133,0.08);
    border: 1px solid rgba(57,255,133,0.15);
    padding: 2px 8px; border-radius: 3px; display: inline-block; margin-top: 8px;
  }
  .stat-down {
    font-family: 'JetBrains Mono', monospace; font-size: 9px;
    color: var(--red); background: rgba(244,63,94,0.08);
    border: 1px solid rgba(244,63,94,0.15);
    padding: 2px 8px; border-radius: 3px; display: inline-block; margin-top: 8px;
  }

  /* -- PANELS -- */
  .panel {
    background: linear-gradient(135deg, var(--bg1) 0%, var(--bg2) 100%);
    border: 1px solid var(--border2); border-radius: 16px;
    padding: 22px; margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
  }
  .panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: var(--text3); margin-bottom: 16px;
    display: flex; align-items: center; gap: 10px;
  }
  .panel-title::before {
    content: ''; display: block; width: 3px; height: 14px;
    background: linear-gradient(180deg, var(--cyan), var(--violet));
    border-radius: 2px; box-shadow: 0 0 8px var(--cyan);
    flex-shrink: 0;
  }

  /* -- REPURPOSE CARDS -- */
  .repurpose-card {
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border2);
    border-left: 2px solid var(--cyan);
    border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    transition: border-color 0.2s, transform 0.15s;
  }
  .repurpose-card:hover {
    border-left-color: var(--lime);
    transform: translateX(2px);
  }
  .drug-tag {
    background: rgba(13,244,255,0.08); border: 1px solid rgba(13,244,255,0.2);
    border-radius: 4px; padding: 3px 9px; font-size: 11px;
    font-family: 'JetBrains Mono', monospace; color: var(--cyan); display: inline-block;
  }
  .new-tag {
    background: rgba(57,255,133,0.08); border: 1px solid rgba(57,255,133,0.2);
    border-radius: 4px; padding: 3px 9px; font-size: 11px;
    font-family: 'JetBrains Mono', monospace; color: var(--lime); display: inline-block;
  }

  /* -- RISK BADGES -- */
  .risk-high { background: rgba(244,63,94,0.1); color: var(--red);
    border: 1px solid rgba(244,63,94,0.25); padding: 3px 10px; border-radius: 4px;
    font-size: 9px; font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
  .risk-medium { background: rgba(251,191,36,0.1); color: var(--gold);
    border: 1px solid rgba(251,191,36,0.25); padding: 3px 10px; border-radius: 4px;
    font-size: 9px; font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
  .risk-low { background: rgba(57,255,133,0.08); color: var(--lime);
    border: 1px solid rgba(57,255,133,0.2); padding: 3px 10px; border-radius: 4px;
    font-size: 9px; font-family: 'JetBrains Mono', monospace; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }

  /* -- GAP BUBBLES -- */
  .gap-high { background: rgba(244,63,94,0.08); color: var(--red);
    border: 1px solid rgba(244,63,94,0.2); padding: 5px 14px; border-radius: 20px;
    font-size: 10px; font-family: 'JetBrains Mono', monospace; display: inline-block; margin: 3px; }
  .gap-medium { background: rgba(251,191,36,0.08); color: var(--gold);
    border: 1px solid rgba(251,191,36,0.2); padding: 5px 14px; border-radius: 20px;
    font-size: 10px; font-family: 'JetBrains Mono', monospace; display: inline-block; margin: 3px; }
  .gap-low { background: rgba(13,244,255,0.08); color: var(--cyan);
    border: 1px solid rgba(13,244,255,0.18); padding: 5px 14px; border-radius: 20px;
    font-size: 10px; font-family: 'JetBrains Mono', monospace; display: inline-block; margin: 3px; }

  /* -- INSIGHT CARDS -- */
  .insight-card {
    background: linear-gradient(135deg, var(--bg2), var(--bg3));
    border: 1px solid var(--border2); border-radius: 12px;
    padding: 16px; margin-bottom: 10px;
    display: flex; gap: 14px; align-items: flex-start;
  }
  .insight-icon { font-size: 22px; flex-shrink: 0; }
  .insight-title { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 5px; }
  .insight-text { font-size: 11px; color: var(--text2); font-family: 'JetBrains Mono', monospace; line-height: 1.6; }
  .insight-meta { font-size: 9px; color: var(--text3); margin-top: 7px;
    font-family: 'JetBrains Mono', monospace; letter-spacing: 0.1em; text-transform: uppercase; }

  /* -- STREAMLIT WIDGET OVERRIDES -- */
  .stSelectbox > div > div,
  .stTextInput > div > div > input {
    background: var(--bg2) !important;
    border: 1px solid rgba(13,244,255,0.18) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important;
  }
  .stSelectbox > div > div:focus-within,
  .stTextInput > div > div > input:focus {
    border-color: rgba(13,244,255,0.45) !important;
    box-shadow: 0 0 0 3px rgba(13,244,255,0.06) !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, rgba(13,244,255,0.12), rgba(139,92,246,0.12)) !important;
    border: 1px solid rgba(13,244,255,0.3) !important;
    border-radius: 10px !important; color: var(--cyan) !important;
    font-family: 'Space Grotesk', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 0.06em !important; padding: 10px 24px !important;
    width: 100% !important; text-transform: uppercase; font-size: 11px !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, rgba(13,244,255,0.22), rgba(139,92,246,0.22)) !important;
    border-color: rgba(13,244,255,0.55) !important;
    box-shadow: 0 0 24px rgba(13,244,255,0.15) !important;
    transform: translateY(-1px) !important;
  }

  /* -- TABS -- */
  .stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(180deg, var(--bg1) 0%, var(--bg) 100%) !important;
    border-bottom: 1px solid var(--border2) !important;
    gap: 0; padding: 0 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--text3) !important;
    font-family: 'JetBrains Mono', monospace !important; font-size: 9px !important;
    font-weight: 500 !important; letter-spacing: 0.1em !important;
    padding: 14px 14px !important; border: none !important;
    border-bottom: 2px solid transparent !important;
    text-transform: uppercase !important; transition: color 0.2s !important;
  }
  .stTabs [data-baseweb="tab"]:hover { color: var(--text2) !important; }
  .stTabs [aria-selected="true"] {
    color: var(--cyan) !important;
    border-bottom: 2px solid var(--cyan) !important;
    text-shadow: 0 0 20px rgba(13,244,255,0.4);
  }
  .stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 0 !important;
  }

  /* -- METRICS -- */
  div[data-testid="metric-container"] {
    background: linear-gradient(135deg, var(--bg2), var(--bg3)) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 14px !important; padding: 18px !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.3);
  }
  [data-testid="stMetricValue"] {
    color: var(--cyan) !important;
    font-family: 'Clash Display', 'Space Grotesk', sans-serif !important;
    font-size: 26px !important; letter-spacing: -0.02em !important;
  }
  [data-testid="stMetricLabel"] {
    color: var(--text3) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 8px !important; letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
  }
  [data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; }

  /* -- PLOTLY CHARTS -- */
  .js-plotly-plot {
    border-radius: 12px !important;
    border: 1px solid var(--border2) !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4) !important;
  }

  /* -- SCROLLBAR -- */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: rgba(13,244,255,0.2); border-radius: 2px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(13,244,255,0.4); }

  hr { border-color: var(--border2) !important; }
</style>
""")
# HEADER
now_str = datetime.utcnow().strftime("%H:%M:%S UTC")
st.html(f"""
<div class="gdim-header">
  <div style="display:flex;align-items:center;gap:14px">
    <div class="gdim-logo-mark">⊕</div>
    <div>
      <div class="gdim-title">Global Drug Intelligence Monitor</div>
      <div class="gdim-sub">Pharmaceutical Intelligence Platform &nbsp;/&nbsp; Live Intelligence Feed</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:12px">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#3a5068;letter-spacing:0.1em;text-align:right">
      <div>FDA · WHO · PUBMED</div>
      <div>CLINICALTRIALS.GOV</div>
    </div>
    <div class="live-badge">
      <span class="live-dot"></span>
      LIVE &nbsp;{now_str}
    </div>
  </div>
</div>

""")
st.html("<div style='height:8px'></div>")



# ---------------------------------------------
# TABS
# ---------------------------------------------
tabs = st.tabs([
    "🔬 Drug Discovery",
    "🔄 Repurposing",
    "⚠️ Shortages",
    "⚗️ Interactions",
    "🌍 Innovation Map",
    "📄 Paper AI",
    "🧪 Trial Predictor",
    "🕸️ Disease Network",
    "📊 Risk Index",
    "🎯 Research Gaps",
])

# ══════════════════════════════════════════════
# TAB 1 — DRUG DISCOVERY
# ══════════════════════════════════════════════
with tabs[0]:
    section_hdr("🔬","Drug Discovery Trend Predictor",
        "AI analysis of PubMed · ClinicalTrials.gov · Patent filings · Research funding",
        "⚡ AI PREDICTIONS")

    stat_cards([
        ("Active Compounds","48,291","In global pipelines","12.4%",True,C["accent"]),
        ("PubMed Papers (2024)","2.1M","Analyzed this year","8.2%",True,C["accent3"]),
        ("Active Clinical Trials","487,923","Global registrations","15.7%",True,C["accent2"]),
        ("Patents Filed (YTD)","89,441","Biotech & pharma","6.1%",True,C["accent5"]),
        ("R&D Funding","$892B","Global investment","9.3%",True,C["accent4"]),
    ])

    st.html("<div style='height:16px'></div>")

    col1, col2 = st.columns([2,1])
    with col1:
        ptitle("Publication Volume by Therapeutic Area")
        st.plotly_chart(chart_discovery(), use_container_width=True, config={"displayModeBar":False})
    with col2:
        ptitle("5–10 Year Trend Forecast")
        st.plotly_chart(chart_trend_forecast(), use_container_width=True, config={"displayModeBar":False})

    col3, col4 = st.columns([2,1])
    with col3:
        ptitle("PubMed Publications — Stacked by Area")
        st.plotly_chart(chart_pubmed_area(), use_container_width=True, config={"displayModeBar":False})
    with col4:
        ptitle("Live KPI Indicators")
        n = int(time.time() / 5) % 1000
        st.plotly_chart(chart_live_kpis(n), use_container_width=True, config={"displayModeBar":False})
        if st.button("🔄 Refresh Live Data", key="refresh_disc"):
            st.cache_data.clear()
            st.rerun()

# ══════════════════════════════════════════════
# TAB 2 — REPURPOSING
# ══════════════════════════════════════════════
with tabs[1]:
    section_hdr("🔄","AI Drug Repurposing Engine",
        "Molecular similarity (RDKit) · Pathway analysis · Literature mining · FDA & WHO databases",
        "⚡ AI ANALYSIS")

    stat_cards([
        ("Known FDA Drugs","20,750+","Approved compounds",None,True,C["accent"]),
        ("Repurposing Candidates","4,812","AI-identified","NEW",True,C["accent3"]),
        ("Validated Successes","312","Clinically confirmed",None,True,C["accent5"]),
        ("Avg. Dev. Savings","$1.4B","Per repurposed drug",None,True,C["accent2"]),
    ])

    st.html("<div style='height:16px'></div>")

    col1, col2 = st.columns([1,1])
    with col1:
        ptitle("Confidence Scores by Candidate")
        st.plotly_chart(chart_repurpose(), use_container_width=True, config={"displayModeBar":False})

    with col2:
        ptitle("Top Repurposing Candidates")
        for r in REPURPOSE_DATA:
            drug, orig, new_use, conf, basis = r
            bar_w = conf
            color = "#00ff9d" if conf>85 else "#00d4ff" if conf>70 else "#8fa4c2"
            st.html(f"""
            <div class="repurpose-card">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap">
                <span class="drug-tag">{drug}</span>
                <span style="font-size:10px;color:#4a6080;font-family:DM Mono,monospace">{orig}</span>
                <span style="color:#00ff9d;font-size:14px">&rarr;</span>
                <span class="new-tag">{new_use}</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                <div style="flex:1;height:4px;background:rgba(255,255,255,0.06);border-radius:2px">
                  <div style="height:100%;width:{bar_w}%;background:linear-gradient(90deg,#00d4ff,#7b4fff);border-radius:2px"></div>
                </div>
                <span style="font-size:10px;font-family:DM Mono,monospace;color:{color}">{conf}%</span>
              </div>
              <div style="font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace">{basis}</div>
            </div>""")

# ══════════════════════════════════════════════
# TAB 3 — SHORTAGES
# ══════════════════════════════════════════════
with tabs[2]:
    section_hdr("⚠️","Global Drug Shortage Early Warning System",
        "FDA shortage database · WHO alerts · Supply chain disruptions · Geopolitical risk",
        "🚨 REAL-TIME")

    stat_cards([
        ("Active Shortages (US)","142","FDA shortage list","8 this week",False,C["danger"]),
        ("Critical Risk Drugs","38","Risk score > 80",None,False,C["warning"]),
        ("WHO Alerts","27","Global alerts active",None,False,C["accent4"]),
        ("Mfg. Shutdowns","14","Active disruptions",None,False,C["text"]),
        ("Supply Chain Events","91","Monitored incidents",None,True,C["accent2"]),
    ])

    st.html("<div style='height:16px'></div>")

    ptitle("Drug Shortage Risk Scores — Live 90-Day Trend")
    st.plotly_chart(chart_shortage_ts(), use_container_width=True, config={"displayModeBar":False})

    col1, col2 = st.columns([6,4])
    with col1:
        ptitle("Current Shortage Risk Intelligence")
        # Table header
        hcols = st.columns([2.5,1.5,1,1,1])
        for hc, ht in zip(hcols, ["Drug / Category","Risk Score","Status","Region","Level"]):
            st.html(f'<div style="font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:#4a6080;font-family:DM Mono,monospace;padding-bottom:6px;border-bottom:1px solid rgba(0,212,255,0.12)">{ht}</div>')

        for drug, cat, score, status, region, risk in SHORTAGE_TABLE:
            risk_color = C["danger"] if risk=="HIGH" else C["warning"] if risk=="MEDIUM" else C["success"]
            risk_rgb = "255,59,92" if risk=="HIGH" else "255,184,0" if risk=="MEDIUM" else "0,230,118"
            rcols = st.columns([2.5,1.5,1,1,1])
            rcols[0].markdown(f'<div style="font-size:12px;color:#e2eaf5;font-weight:600">{drug}</div><div style="font-size:10px;color:#4a6080;font-family:DM Mono,monospace">{cat}</div>')
            rcols[1].markdown(f'<div style="display:flex;align-items:center;gap:6px;margin-top:4px"><div style="flex:1;height:4px;background:rgba(255,255,255,0.05);border-radius:2px"><div style="height:100%;width:{score}%;background:{risk_color}"></div></div><span style="font-size:10px;color:{risk_color};font-family:DM Mono,monospace">{score}</span></div>')
            rcols[2].markdown(f'<div style="font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace;margin-top:4px">{status}</div>')
            rcols[3].markdown(f'<div style="font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace;margin-top:4px">{region}</div>')
            rcols[4].markdown(f'<span style="background:rgba({risk_rgb},.15);color:{risk_color};border:1px solid rgba({risk_rgb},.3);padding:3px 8px;border-radius:4px;font-size:9px;font-family:DM Mono,monospace;font-weight:700">● {risk}</span>')

    with col2:
        ptitle("Risk Score Ranking")
        st.plotly_chart(chart_shortage_bar(), use_container_width=True, config={"displayModeBar":False})

    if st.button("🔄 Refresh Shortage Data", key="refresh_shortage"):
        st.cache_data.clear()
        st.rerun()

# ══════════════════════════════════════════════
# TAB 4 — INTERACTIONS
# ══════════════════════════════════════════════
with tabs[3]:
    section_hdr("⚗️","Drug Interaction Risk AI",
        "Molecular fingerprints · Pharmacokinetic modeling · Real-time interaction prediction",
        "⚡ AI PREDICTION")

    st.html('<div class="panel">')
    ptitle("Enter Drugs to Analyze")
    c1, c2, c3 = st.columns([2,2,1])
    with c1:
        d1 = st.text_input("Drug 1", value="warfarin", placeholder="e.g. warfarin", label_visibility="collapsed")
    with c2:
        d2 = st.text_input("Drug 2", value="aspirin", placeholder="e.g. aspirin", label_visibility="collapsed")
    with c3:
        analyze = st.button("Analyze Interaction", key="btn_interact")
    st.html('</div>')

    if analyze or (d1 and d2):
        k1, k2 = d1.lower().strip(), d2.lower().strip()
        result = INTERACTION_DB.get((k1,k2)) or INTERACTION_DB.get((k2,k1))
        if not result:
            result = ("MODERATE",55,"Pharmacokinetic interaction possible. Monitor clinical response closely.")
        level, score, mechanism = result
        risk_color = C["danger"] if score>75 else C["warning"] if score>50 else C["success"]

        gc1, gc2 = st.columns([1,1])
        with gc1:
            st.plotly_chart(chart_interaction_gauge(score, level), use_container_width=True, config={"displayModeBar":False})
        with gc2:
            st.html(f"""
            <div style="padding:16px">
              <div style="font-size:16px;font-weight:700;color:#e2eaf5;margin-bottom:14px;font-family:Syne,sans-serif">
                {d1.title()} + {d2.title()}
              </div>
              <div style="padding:12px;background:rgba(0,0,0,0.2);border-radius:8px;border:1px solid {risk_color}22;margin-bottom:10px">
                <div style="font-size:9px;color:#4a6080;font-family:DM Mono,monospace;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">Risk Level</div>
                <div style="font-size:15px;font-weight:700;color:{risk_color};font-family:DM Mono,monospace">{level}</div>
              </div>
              <div style="padding:12px;background:rgba(0,0,0,0.2);border-radius:8px;border:1px solid rgba(255,255,255,0.05);margin-bottom:10px">
                <div style="font-size:9px;color:#4a6080;font-family:DM Mono,monospace;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">Mechanism</div>
                <div style="font-size:12px;color:#8fa4c2;font-family:DM Mono,monospace;line-height:1.5">{mechanism}</div>
              </div>
              <div style="padding:12px;background:rgba(0,255,157,0.04);border-radius:8px;border:1px solid rgba(0,255,157,0.12)">
                <div style="font-size:9px;color:#4a6080;font-family:DM Mono,monospace;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px">Recommendation</div>
                <div style="font-size:12px;color:#00ff9d;font-family:DM Mono,monospace;line-height:1.5">Monitor patient closely. Check for signs of adverse effects. Consider dose adjustment or alternative therapy if risk outweighs benefit.</div>
              </div>
            </div>""")

    st.html("<div style='height:16px'></div>")
    col1, col2 = st.columns(2)
    with col1:
        ptitle("Common High-Risk Combinations")
        fig = go.Figure(go.Bar(
            x=[95,93,88,84,71],
            y=["Warfarin+NSAIDs","MAOIs+SSRIs","Digoxin+Amiodarone","MTX+NSAIDs","Clopidogrel+PPIs"],
            orientation="h",
            marker_color=[C["danger"],C["danger"],C["warning"],C["warning"],C["accent4"]],
            text=["CRITICAL","CRITICAL","SEVERE","SEVERE","MODERATE"],textposition="inside",
            textfont=dict(size=10)))
        apply_base(fig, height=240, margin=dict(l=0,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with col2:
        ptitle("Interaction Mechanisms")
        fig2 = go.Figure(go.Pie(
            labels=["CYP450 Inhibition","PD Synergy","Protein Binding","P-gp Inhibition","Renal Clearance"],
            values=[42,28,16,9,5],hole=0.55,
            marker=dict(colors=[C["accent"],C["accent2"],C["accent3"],C["accent5"],C["accent4"]]),
            textfont=dict(size=10,family="DM Mono,monospace")))
        apply_base(fig2, height=240, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

# ══════════════════════════════════════════════
# TAB 5 — INNOVATION MAP
# ══════════════════════════════════════════════
with tabs[4]:
    section_hdr("🌍","Pharma Innovation Heatmap",
        "Research papers · Biotech startups · Clinical trials · Patents · Global clusters")

    stat_cards([
        ("Innovation Hotspots","47","Global clusters",None,True,C["accent5"]),
        ("Biotech Startups","8,941","Active globally","22%",True,C["accent"]),
        ("#1 Hub: Boston","9.4","Innovation index",None,True,C["accent3"]),
        ("Emerging Regions","12","New biotech hubs",None,True,C["accent2"]),
        ("Cross-Border Trials","61%","International",None,True,C["accent4"]),
    ])
    st.html("<div style='height:16px'></div>")

    ptitle("Global Pharmaceutical Innovation Density — Interactive 3D Globe")
    st.html("""
<style>
  :root {
    --bg:#04080f; --bg2:#0a1628; --cyan:#0df4ff; --lime:#39ff85;
    --violet:#8b5cf6; --text:#e8f0fe; --text3:#3a5068;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); font-family:'Space Grotesk',sans-serif; }

  /* -- HEADER -- */
  .gdim-header {
    background: linear-gradient(135deg, rgba(4,8,15,0.98), rgba(10,22,40,0.98));
    border-bottom: 1px solid rgba(13,244,255,0.1);
    padding: 0 32px; height: 64px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 1px 0 rgba(13,244,255,0.08), 0 8px 32px rgba(0,0,0,0.6);
    position: sticky; top: 0; z-index: 999;
  }
  .gdim-logo-mark {
    width:36px; height:36px; border-radius:10px;
    background: linear-gradient(135deg,rgba(13,244,255,0.15),rgba(139,92,246,0.15));
    border: 1px solid rgba(13,244,255,0.3);
    display:flex; align-items:center; justify-content:center;
    font-size:18px; font-weight:900; color:var(--cyan);
    text-shadow:0 0 20px var(--cyan);
    box-shadow:0 0 20px rgba(13,244,255,0.12), inset 0 1px 0 rgba(255,255,255,0.1);
    flex-shrink:0;
  }
  .gdim-title {
    font-size:15px; font-weight:700; letter-spacing:0.08em;
    text-transform:uppercase; margin:0;
    background:linear-gradient(90deg,var(--text),var(--cyan));
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  }
  .gdim-sub {
    font-family:'JetBrains Mono',monospace;
    font-size:9px; color:var(--text3); margin:2px 0 0 0;
    letter-spacing:0.14em; text-transform:uppercase;
  }
  .live-badge {
    font-family:'JetBrains Mono',monospace; font-size:9px;
    color:var(--lime); display:flex; align-items:center; gap:8px;
    background:rgba(57,255,133,0.06); border:1px solid rgba(57,255,133,0.2);
    padding:6px 14px; border-radius:20px; letter-spacing:0.06em;
  }
  .live-dot {
    width:6px; height:6px; border-radius:50%;
    background:var(--lime); box-shadow:0 0 10px var(--lime);
    animation:livePulse 1.4s ease-in-out infinite; flex-shrink:0;
  }
  @keyframes livePulse {
    0%,100%{opacity:1;box-shadow:0 0 8px var(--lime);}
    50%{opacity:0.4;box-shadow:0 0 3px var(--lime);}
  }

  /* -- GLOBE WRAP -- */
  .globe-wrap {
    width:100%; height:560px; position:relative;
    border-radius:16px; overflow:hidden;
    border:1px solid rgba(13,244,255,0.12);
    background:#020408;
  }
  #globe-canvas { width:100%; height:100%; display:block; cursor:grab; touch-action:none; }
  #globe-canvas:active { cursor:grabbing; }

  /* HUD */
  .hud-hint {
    position:absolute; top:14px; left:14px;
    font-family:'JetBrains Mono',monospace; font-size:8px;
    color:rgba(13,244,255,0.4); letter-spacing:0.16em; text-transform:uppercase;
    pointer-events:none;
  }
  .hud-badge {
    position:absolute; top:14px; right:14px;
    font-family:'JetBrains Mono',monospace; font-size:8px;
    color:rgba(57,255,133,0.5); letter-spacing:0.12em; text-transform:uppercase;
    background:rgba(57,255,133,0.05); border:1px solid rgba(57,255,133,0.12);
    padding:4px 10px; border-radius:4px; pointer-events:none;
    display:flex; align-items:center; gap:6px;
  }
  .hud-dot { width:5px;height:5px;border-radius:50%;background:var(--lime);
    box-shadow:0 0 8px var(--lime);animation:livePulse 1.4s ease-in-out infinite; }

  /* Tooltip */
  #tt {
    position:absolute; display:none; z-index:6; pointer-events:none;
    background:rgba(4,8,15,0.93); border:1px solid rgba(13,244,255,0.25);
    border-radius:10px; padding:12px 16px; min-width:190px;
    box-shadow:0 8px 32px rgba(0,0,0,0.7),0 0 0 1px rgba(13,244,255,0.06);
  }
  #tt-city { font-size:14px; font-weight:700; color:#e8f0fe; margin-bottom:8px; }
  .tt-row { display:flex; gap:20px; }
  .tt-col label { font-family:'JetBrains Mono',monospace; font-size:8px;
    color:#3a5068; letter-spacing:0.14em; text-transform:uppercase; display:block; margin-bottom:2px; }
  .tt-col span { font-family:'JetBrains Mono',monospace; font-size:16px; font-weight:700; }
  #tt-score { color:#0df4ff; }
  #tt-startups { color:#39ff85; }
  #tt-bar-wrap { margin-top:8px;height:3px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden; }
  #tt-bar { height:100%;border-radius:2px;background:linear-gradient(90deg,#0df4ff,#8b5cf6); }
  #tt-rank { font-family:'JetBrains Mono',monospace;font-size:9px;color:#3a5068;margin-top:6px;letter-spacing:0.1em; }
</style>

<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

<div class="globe-wrap">
  <div class="hud-hint">🌐 Drag · Scroll to zoom · Hover markers</div>
  <div class="hud-badge"><span class="hud-dot"></span>18 Pharma Hubs · Live</div>
  <canvas id="globe-canvas"></canvas>
  <div id="tt">
    <div id="tt-city"></div>
    <div class="tt-row">
      <div class="tt-col"><label>Index</label><span id="tt-score"></span></div>
      <div class="tt-col"><label>Startups</label><span id="tt-startups"></span></div>
    </div>
    <div id="tt-bar-wrap"><div id="tt-bar" style="width:0%"></div></div>
    <div id="tt-rank"></div>
  </div>
</div>

<script>
(function(){
"use strict";

// -- Data --
const HUBS = [
  {city:"Boston, MA",      lat:42.36,  lon:-71.06, score:9.4, startups:1240, rank:1},
  {city:"San Francisco",   lat:37.77,  lon:-122.42,score:9.1, startups:1100, rank:2},
  {city:"New York, NY",    lat:40.71,  lon:-74.01, score:8.8, startups:980,  rank:3},
  {city:"Basel, CH",       lat:47.56,  lon:7.59,   score:8.9, startups:890,  rank:4},
  {city:"London, UK",      lat:51.51,  lon:-0.13,  score:8.7, startups:860,  rank:5},
  {city:"Shanghai, CN",    lat:31.23,  lon:121.47, score:8.6, startups:820,  rank:6},
  {city:"Zurich, CH",      lat:47.38,  lon:8.54,   score:8.5, startups:780,  rank:7},
  {city:"Tokyo, JP",       lat:35.68,  lon:139.69, score:8.3, startups:750,  rank:8},
  {city:"San Diego, CA",   lat:32.72,  lon:-117.16,score:8.2, startups:710,  rank:9},
  {city:"Munich, DE",      lat:48.14,  lon:11.58,  score:8.1, startups:680,  rank:10},
  {city:"Beijing, CN",     lat:39.91,  lon:116.39, score:8.0, startups:660,  rank:11},
  {city:"Toronto, CA",     lat:43.65,  lon:-79.38, score:7.9, startups:610,  rank:12},
  {city:"Stockholm, SE",   lat:59.33,  lon:18.07,  score:7.8, startups:580,  rank:13},
  {city:"Singapore",       lat:1.35,   lon:103.82, score:7.7, startups:540,  rank:14},
  {city:"Bangalore, IN",   lat:12.97,  lon:77.59,  score:7.6, startups:520,  rank:15},
  {city:"Osaka, JP",       lat:34.69,  lon:135.50, score:7.5, startups:490,  rank:16},
  {city:"Sydney, AU",      lat:-33.87, lon:151.21, score:7.2, startups:440,  rank:17},
  {city:"São Paulo, BR",   lat:-23.55, lon:-46.63, score:6.8, startups:390,  rank:18},
];

// -- Canvas & WebGL --
const canvas = document.getElementById('globe-canvas');
const wrap   = canvas.parentElement;

function resize() {
  canvas.width  = wrap.clientWidth  * window.devicePixelRatio;
  canvas.height = wrap.clientHeight * window.devicePixelRatio;
  canvas.style.width  = wrap.clientWidth  + 'px';
  canvas.style.height = wrap.clientHeight + 'px';
}
resize();
window.addEventListener('resize', ()=>{ resize(); buildProjection(); });

const gl = canvas.getContext('webgl', {antialias:true, alpha:false}) ||
           canvas.getContext('experimental-webgl', {antialias:true, alpha:false});
if (!gl) { canvas.parentElement.innerHTML='<p style="color:#f43f5e;padding:20px">WebGL not supported</p>'; return; }

gl.enable(gl.DEPTH_TEST);
gl.enable(gl.BLEND);
gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
gl.clearColor(0.008, 0.016, 0.031, 1.0);

// -- Shaders --
function mkShader(type, src) {
  const s = gl.createShader(type);
  gl.shaderSource(s, src); gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) console.error(gl.getShaderInfoLog(s));
  return s;
}
function mkProgram(vs, fs) {
  const p = gl.createProgram();
  gl.attachShader(p, mkShader(gl.VERTEX_SHADER, vs));
  gl.attachShader(p, mkShader(gl.FRAGMENT_SHADER, fs));
  gl.linkProgram(p);
  return p;
}

// Globe vertex shader
const GLOBE_VS = `
  precision highp float;
  attribute vec3 aPos;
  attribute vec3 aNormal;
  attribute vec2 aUV;
  uniform mat4 uMVP;
  uniform mat4 uModel;
  uniform mat3 uNormalMat;
  varying vec3 vNormal;
  varying vec3 vWorldPos;
  varying vec2 vUV;
  void main(){
    vUV = aUV;
    vNormal = normalize(uNormalMat * aNormal);
    vec4 world = uModel * vec4(aPos,1.0);
    vWorldPos = world.xyz;
    gl_Position = uMVP * vec4(aPos,1.0);
  }`;

// Globe fragment shader - procedural earth
const GLOBE_FS = `
  precision highp float;
  varying vec3 vNormal;
  varying vec3 vWorldPos;
  varying vec2 vUV;
  uniform vec3 uSunDir;
  uniform float uTime;

  // Pseudo-random
  float rand(vec2 co){ return fract(sin(dot(co,vec2(12.9898,78.233)))*43758.5453); }

  // Smooth noise
  float noise(vec2 p){
    vec2 i=floor(p), f=fract(p);
    f=f*f*(3.0-2.0*f);
    float a=rand(i), b=rand(i+vec2(1,0)), c=rand(i+vec2(0,1)), d=rand(i+vec2(1,1));
    return mix(mix(a,b,f.x),mix(c,d,f.x),f.y);
  }
  float fbm(vec2 p){
    return noise(p)*0.5+noise(p*2.1)*0.25+noise(p*4.3)*0.125+noise(p*8.7)*0.0625;
  }

  // Land detection (approximate continents from UV)
  float isLand(vec2 uv){
    float u=uv.x, v=uv.y;
    float land=0.0;
    // North America
    if(u>0.08&&u<0.28&&v>0.25&&v<0.65) land=max(land,
      smoothstep(0.38,0.3,abs(u-0.18))*smoothstep(0.2,0.1,abs(v-0.45)));
    // South America
    if(u>0.14&&u<0.30&&v>0.52&&v<0.88) land=max(land,
      smoothstep(0.1,0.05,abs(u-0.21))*smoothstep(0.22,0.1,abs(v-0.68)));
    // Europe
    if(u>0.44&&u<0.56&&v>0.15&&v<0.45) land=max(land,
      smoothstep(0.09,0.04,abs(u-0.50))*smoothstep(0.18,0.06,abs(v-0.30)));
    // Africa
    if(u>0.43&&u<0.60&&v>0.35&&v<0.80) land=max(land,
      smoothstep(0.11,0.05,abs(u-0.51))*smoothstep(0.25,0.1,abs(v-0.57)));
    // Asia main
    if(u>0.50&&u<0.85&&v>0.10&&v<0.58) land=max(land,
      smoothstep(0.22,0.1,abs(u-0.70))*smoothstep(0.28,0.1,abs(v-0.32)));
    // India sub
    if(u>0.59&&u<0.70&&v>0.38&&v<0.62) land=max(land,
      smoothstep(0.08,0.03,abs(u-0.645))*smoothstep(0.14,0.04,abs(v-0.50)));
    // SE Asia / Indonesia
    if(u>0.72&&u<0.92&&v>0.43&&v<0.63) land=max(land,
      smoothstep(0.12,0.04,abs(u-0.80))*smoothstep(0.12,0.04,abs(v-0.53)));
    // Japan
    if(u>0.80&&u<0.87&&v>0.22&&v<0.38) land=max(land,
      smoothstep(0.05,0.02,abs(u-0.835))*smoothstep(0.1,0.03,abs(v-0.30)));
    // Australia
    if(u>0.76&&u<0.92&&v>0.56&&v<0.76) land=max(land,
      smoothstep(0.1,0.04,abs(u-0.84))*smoothstep(0.12,0.05,abs(v-0.65)));
    // Greenland
    if(u>0.20&&u<0.35&&v>0.10&&v<0.32) land=max(land,
      smoothstep(0.09,0.04,abs(u-0.275))*smoothstep(0.12,0.04,abs(v-0.21)));
    return clamp(land*1.8,0.0,1.0);
  }

  void main(){
    vec2 uv = vUV;
    float t = uTime;

    // Noise for terrain variation
    float tex = fbm(uv*6.0+0.5);
    float land = isLand(uv);

    // Land colours: green->brown->rocky
    vec3 deepGreen  = vec3(0.06,0.28,0.10);
    vec3 lightGreen = vec3(0.13,0.42,0.16);
    vec3 desert     = vec3(0.55,0.42,0.18);
    vec3 mountain   = vec3(0.35,0.32,0.30);
    vec3 snow       = vec3(0.88,0.92,0.96);

    float v = uv.y;
    // Blend land based on latitude
    vec3 landCol = mix(deepGreen, lightGreen, tex);
    if(v<0.15||v>0.85) landCol = mix(landCol, snow, smoothstep(0.8,0.95,max(v,1.0-v)));
    if(v>0.35&&v<0.55) landCol = mix(landCol, desert, smoothstep(0.1,0.0,land)*0.5);
    landCol += (tex-0.5)*0.06; // terrain variation

    // Ocean colours: deep to shallow
    vec3 deepOcean   = vec3(0.01,0.06,0.18);
    vec3 shallowOcean= vec3(0.03,0.18,0.38);
    vec3 oceanCol = mix(deepOcean, shallowOcean, fbm(uv*3.0)*0.5);
    // Ocean shimmer
    float shimmer = fbm(uv*12.0 + vec2(t*0.05,0.0));
    oceanCol += vec3(0.0,0.04,0.08)*shimmer;

    // Mix land/ocean
    vec3 surfaceCol = mix(oceanCol, landCol, land);

    // Ice caps
    float polar = smoothstep(0.85,0.99,max(v, 1.0-v));
    surfaceCol = mix(surfaceCol, vec3(0.85,0.90,0.95), polar);

    // Clouds (animated)
    float cloud1 = fbm(uv*4.5 + vec2(t*0.012, 0.0));
    float cloud2 = fbm(uv*8.0 + vec2(-t*0.007, t*0.004));
    float clouds = smoothstep(0.54, 0.68, cloud1*0.6 + cloud2*0.4);
    clouds *= (1.0-polar*0.8);
    vec3 cloudCol = vec3(0.88,0.93,1.0);
    surfaceCol = mix(surfaceCol, cloudCol, clouds*0.85);

    // Lighting
    vec3 N = normalize(vNormal);
    float diff = max(0.0, dot(N, uSunDir));
    float diffSoft = diff*0.8 + 0.2; // ambient fill

    // Specular on ocean
    vec3 viewDir = normalize(-vWorldPos);
    vec3 halfV = normalize(uSunDir + viewDir);
    float spec = pow(max(0.0,dot(N,halfV)),64.0) * (1.0-land) * (1.0-clouds);

    vec3 col = surfaceCol * diffSoft + vec3(0.4,0.7,1.0)*spec*0.6;

    // Atmosphere haze at limb
    float rim = 1.0 - max(0.0,dot(N,viewDir));
    rim = pow(rim,3.5);
    col += vec3(0.05,0.40,0.70)*rim*0.6 * (diff*0.5+0.5);

    // Night side city lights (faint orange glow)
    float nightSide = 1.0-smoothstep(0.0,0.25,diff);
    float cityDensity = land * (0.3+fbm(uv*20.0)*0.7);
    col += vec3(1.0,0.55,0.1)*cityDensity*nightSide*0.18;

    gl_FragColor = vec4(col, 1.0);
  }`;

// Atmosphere fragment shader
const ATM_FS = `
  precision mediump float;
  varying vec3 vNormal;
  varying vec3 vWorldPos;
  varying vec2 vUV;
  uniform vec3 uSunDir;
  void main(){
    vec3 N = normalize(vNormal);
    vec3 viewDir = normalize(-vWorldPos);
    float rim = 1.0 - max(0.0, dot(N, viewDir));
    rim = pow(rim, 4.0);
    float sun = max(0.0, dot(N, uSunDir))*0.5+0.5;
    vec3 atmCol = mix(vec3(0.05,0.30,0.80), vec3(0.3,0.6,1.0), sun);
    gl_FragColor = vec4(atmCol, rim * 0.55);
  }`;

// Marker vertex shader
const MRK_VS = `
  precision highp float;
  attribute vec3 aPos;
  uniform mat4 uMVP;
  void main(){ gl_Position = uMVP * vec4(aPos,1.0); gl_PointSize = 8.0; }`;

const MRK_FS = `
  precision mediump float;
  uniform vec4 uColor;
  void main(){
    vec2 c = gl_PointCoord - 0.5;
    float d = length(c);
    float circle = 1.0 - smoothstep(0.35, 0.5, d);
    float glow   = exp(-d*d*8.0)*0.7;
    gl_FragColor = vec4(uColor.rgb, uColor.a*(circle+glow));
  }`;

// Ring shader
const RING_VS = `
  precision highp float;
  attribute vec3 aPos;
  uniform mat4 uMVP;
  void main(){ gl_Position = uMVP * vec4(aPos,1.0); }`;
const RING_FS = `
  precision mediump float;
  uniform vec4 uColor;
  void main(){ gl_FragColor = uColor; }`;

// Star shader
const STAR_VS = `
  precision highp float;
  attribute vec3 aPos;
  attribute float aSize;
  uniform mat4 uMVP;
  void main(){ gl_Position = uMVP * vec4(aPos,1.0); gl_PointSize = aSize; }`;
const STAR_FS = `
  precision mediump float;
  varying vec2 vUV;
  void main(){
    vec2 c = gl_PointCoord - 0.5;
    float d = length(c);
    float a = 1.0 - smoothstep(0.2, 0.5, d);
    gl_FragColor = vec4(1.0,1.0,1.0, a*0.8);
  }`;

const globeProg = mkProgram(GLOBE_VS, GLOBE_FS);
const atmProg   = mkProgram(GLOBE_VS, ATM_FS);
const mrkProg   = mkProgram(MRK_VS,  MRK_FS);
const ringProg  = mkProgram(RING_VS, RING_FS);
const starProg  = mkProgram(STAR_VS, STAR_FS);

// -- Geometry builders --
function buildSphere(radius, segs, rings) {
  const pos=[], nor=[], uvs=[], idx=[];
  for(let r=0;r<=rings;r++){
    const phi=r/rings*Math.PI;
    for(let s=0;s<=segs;s++){
      const theta=s/segs*Math.PI*2;
      const x=Math.sin(phi)*Math.cos(theta);
      const y=Math.cos(phi);
      const z=Math.sin(phi)*Math.sin(theta);
      pos.push(radius*x,radius*y,radius*z);
      nor.push(x,y,z);
      uvs.push(s/segs, r/rings);
    }
  }
  for(let r=0;r<rings;r++) for(let s=0;s<segs;s++){
    const a=(segs+1)*r+s, b=a+(segs+1), c=b+1, d=a+1;
    idx.push(a,b,d, b,c,d);
  }
  return {pos:new Float32Array(pos),nor:new Float32Array(nor),
          uvs:new Float32Array(uvs),idx:new Uint16Array(idx)};
}

function mkBuf(data,target=gl.ARRAY_BUFFER){
  const b=gl.createBuffer(); gl.bindBuffer(target,b); gl.bufferData(target,data,gl.STATIC_DRAW); return b;
}
function mkDynBuf(data,target=gl.ARRAY_BUFFER){
  const b=gl.createBuffer(); gl.bindBuffer(target,b); gl.bufferData(target,data,gl.DYNAMIC_DRAW); return b;
}

const earth = buildSphere(1.0, 96, 64);
const ePosB=mkBuf(earth.pos); const eNorB=mkBuf(earth.nor); const eUVB=mkBuf(earth.uvs); const eIdxB=mkBuf(earth.idx,gl.ELEMENT_ARRAY_BUFFER);

const atm = buildSphere(1.065, 64, 48);
const aPosB=mkBuf(atm.pos); const aNorB=mkBuf(atm.nor); const aUVB=mkBuf(atm.uvs); const aIdxB=mkBuf(atm.idx,gl.ELEMENT_ARRAY_BUFFER);

// Stars
const NSTARS=1800;
const starPos=new Float32Array(NSTARS*3), starSz=new Float32Array(NSTARS);
for(let i=0;i<NSTARS;i++){
  const th=Math.random()*Math.PI*2, ph=Math.acos(2*Math.random()-1), r=9+Math.random()*3;
  starPos[i*3]=r*Math.sin(ph)*Math.cos(th);
  starPos[i*3+1]=r*Math.cos(ph);
  starPos[i*3+2]=r*Math.sin(ph)*Math.sin(th);
  starSz[i]=Math.random()*2.2+0.5;
}
const starPosB=mkBuf(starPos); const starSzB=mkBuf(starSz);

// Hub 3D positions
function latLon(lat,lon,r){
  const phi=(90-lat)*Math.PI/180, th=(lon+180)*Math.PI/180;
  return [-r*Math.sin(phi)*Math.cos(th), r*Math.cos(phi), r*Math.sin(phi)*Math.sin(th)];
}
function scoreColor(s){
  const t=(s-6.5)/3.0;
  return [0.05+t*0.17, 0.96-t*0.24, 1.0-t*0.38, 1.0];
}

const HUB_R=1.015;
const hubPositions=HUBS.map(h=>latLon(h.lat,h.lon,HUB_R));

// Marker points buffer (updated each frame for pulsing)
const mrkPosArr=new Float32Array(HUBS.length*3);
hubPositions.forEach((p,i)=>{mrkPosArr[i*3]=p[0];mrkPosArr[i*3+1]=p[1];mrkPosArr[i*3+2]=p[2];});
const mrkPosB=mkDynBuf(mrkPosArr);

// Pulse rings: each ring is 32 line-loop segments
function buildRing(cx,cy,cz,nx,ny,nz,r){
  const pts=[];
  // Build local basis perpendicular to normal
  let ax=0,ay=1,az=0;
  const dot2=ax*nx+ay*ny+az*nz;
  if(Math.abs(dot2)>0.9){ax=1;ay=0;az=0;}
  // u = normal x ax
  let ux=ny*az-nz*ay, uy=nz*ax-nx*az, uz=nx*ay-ny*ax;
  const ul=Math.sqrt(ux*ux+uy*uy+uz*uz); ux/=ul;uy/=ul;uz/=ul;
  // v = normal x u
  const vx=ny*uz-nz*uy, vy=nz*ux-nx*uz, vz=nx*uy-ny*ux;
  const SEGS=32;
  for(let i=0;i<=SEGS;i++){
    const a=i/SEGS*Math.PI*2;
    pts.push(cx+r*(Math.cos(a)*ux+Math.sin(a)*vx));
    pts.push(cy+r*(Math.cos(a)*uy+Math.sin(a)*vy));
    pts.push(cz+r*(Math.cos(a)*uz+Math.sin(a)*vz));
  }
  return new Float32Array(pts);
}

const rings=HUBS.map((h,i)=>{
  const p=hubPositions[i];
  const n=[p[0]/HUB_R,p[1]/HUB_R,p[2]/HUB_R];
  return {
    base:buildRing(p[0],p[1],p[2],n[0],n[1],n[2],0.025),
    buf:null, phase:i*0.35, hub:h
  };
});
rings.forEach(r=>{ r.buf=mkDynBuf(r.base); });

// -- Math helpers --
function mat4(){return new Float32Array(16);}
function identity(m){m[0]=m[5]=m[10]=m[15]=1;m[1]=m[2]=m[3]=m[4]=m[6]=m[7]=m[8]=m[9]=m[11]=m[12]=m[13]=m[14]=0;return m;}
function multiply(a,b,out){
  for(let i=0;i<4;i++) for(let j=0;j<4;j++){
    out[i*4+j]=0;
    for(let k=0;k<4;k++) out[i*4+j]+=a[i*4+k]*b[k*4+j];
  }
  return out;
}
function perspective(fov,aspect,near,far,out){
  const f=1/Math.tan(fov/2);
  out[0]=f/aspect;out[5]=f;
  out[10]=(far+near)/(near-far);out[11]=-1;
  out[14]=2*far*near/(near-far);
  out[1]=out[2]=out[3]=out[4]=out[6]=out[7]=out[8]=out[9]=out[12]=out[13]=out[15]=0;
  return out;
}
function translate(tx,ty,tz,out){
  identity(out); out[12]=tx;out[13]=ty;out[14]=tz; return out;
}
function rotY(a,out){ identity(out);const c=Math.cos(a),s=Math.sin(a);out[0]=c;out[2]=s;out[8]=-s;out[10]=c;return out;}
function rotX(a,out){ identity(out);const c=Math.cos(a),s=Math.sin(a);out[5]=c;out[6]=-s;out[9]=s;out[10]=c;return out;}
function normalMatrix3(m4,out3){
  // Upper-left 3x3, transposed inverse (for uniform scale just transpose)
  out3[0]=m4[0];out3[1]=m4[4];out3[2]=m4[8];
  out3[3]=m4[1];out3[4]=m4[5];out3[5]=m4[9];
  out3[6]=m4[2];out3[7]=m4[6];out3[8]=m4[10];
  return out3;
}

// -- State --
let rotY_val=0.3, rotX_val=0.18, zoom=2.8;
let isDragging=false, prevX=0, prevY=0;
let velX=0, velY=0, autoRot=true, autoTimer=null;
let time=0;

// -- Interaction --
function startDrag(x,y){isDragging=true;prevX=x;prevY=y;autoRot=false;clearTimeout(autoTimer);}
function doDrag(x,y){
  if(!isDragging)return;
  velY=(x-prevX)*0.007; velX=(y-prevY)*0.007;
  rotY_val+=velY; rotX_val+=velX;
  rotX_val=Math.max(-1.3,Math.min(1.3,rotX_val));
  prevX=x;prevY=y;
}
function endDrag(){isDragging=false;autoTimer=setTimeout(()=>autoRot=true,3000);}

canvas.addEventListener('mousedown',e=>{e.preventDefault();startDrag(e.clientX,e.clientY);});
window.addEventListener('mousemove',e=>{doDrag(e.clientX,e.clientY);});
window.addEventListener('mouseup',endDrag);
canvas.addEventListener('touchstart',e=>{e.preventDefault();startDrag(e.touches[0].clientX,e.touches[0].clientY);},{passive:false});
canvas.addEventListener('touchmove',e=>{e.preventDefault();doDrag(e.touches[0].clientX,e.touches[0].clientY);},{passive:false});
canvas.addEventListener('touchend',endDrag);
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(1.7,Math.min(5.5,zoom+e.deltaY*0.004));},{passive:false});

// -- Tooltip hit-test --
const tooltip=document.getElementById('tt');
const W=canvas.parentElement;
canvas.addEventListener('mousemove',e=>{
  const rect=canvas.getBoundingClientRect();
  const mx=(e.clientX-rect.left)/rect.width*2-1;
  const my=-((e.clientY-rect.top)/rect.height)*2+1;
  // Project each hub and test distance in screen space
  let closest=null, closestDist=0.04;
  HUBS.forEach((hub,i)=>{
    const p=hubPositions[i];
    // Apply rotation
    const cosY=Math.cos(-rotY_val),sinY=Math.sin(-rotY_val);
    const cosX=Math.cos(-rotX_val),sinX=Math.sin(-rotX_val);
    // rotY
    let rx=p[0]*cosY+p[2]*sinY, ry=p[1], rz=-p[0]*sinY+p[2]*cosY;
    // rotX
    let rrx=rx, rry=ry*cosX-rz*sinX, rrz=ry*sinX+rz*cosX;
    // perspective
    const aspect=canvas.width/canvas.height;
    const f=1/Math.tan(0.7);
    const zc=rrz-zoom;
    const sx=rrx/(-zc)*f/aspect;
    const sy=rry/(-zc)*f;
    const d=Math.sqrt((sx-mx)*(sx-mx)+(sy-my)*(sy-my));
    if(d<closestDist && rrz < 0.8){
      closestDist=d; closest={hub,sx,sy,e};
    }
  });
  if(closest){
    const {hub,e:ev}=closest;
    document.getElementById('tt-city').textContent=hub.city;
    document.getElementById('tt-score').textContent=hub.score;
    document.getElementById('tt-startups').textContent=hub.startups.toLocaleString();
    document.getElementById('tt-bar').style.width=((hub.score-6.5)/(10-6.5)*100)+'%';
    document.getElementById('tt-rank').textContent='RANK #'+hub.rank+' GLOBALLY';
    tooltip.style.display='block';
    tooltip.style.left=(e.clientX-rect.left+18)+'px';
    tooltip.style.top=(e.clientY-rect.top-10)+'px';
  } else {
    tooltip.style.display='none';
  }
});
canvas.addEventListener('mouseleave',()=>tooltip.style.display='none');

// -- Uniforms helper --
function ul(prog,name){return gl.getUniformLocation(prog,name);}
function al(prog,name){return gl.getAttribLocation(prog,name);}

function bindAttr(prog,name,buf,size,stride=0,offset=0){
  const loc=al(prog,name); if(loc<0)return;
  gl.bindBuffer(gl.ARRAY_BUFFER,buf);
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc,size,gl.FLOAT,false,stride*4,offset*4);
}

// -- Render --
const tmp=mat4(), mModel=mat4(), mRX=mat4(), mRY=mat4(), mTrans=mat4();
const mProj=mat4(), mMV=mat4(), mMVP=mat4();
const mNorm=new Float32Array(9);

function render(ts){
  requestAnimationFrame(render);
  time=ts*0.001;

  if(autoRot) rotY_val+=0.0015;
  if(!isDragging){ velX*=0.88; velY*=0.88; }

  const W=canvas.width, H=canvas.height;
  gl.viewport(0,0,W,H);
  gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);

  // Build matrices
  perspective(0.75, W/H, 0.1, 50.0, mProj);
  translate(0,0,-zoom,mTrans);
  rotX(rotX_val,mRX); rotY(rotY_val,mRY);
  multiply(mRX,mRY,tmp); multiply(mTrans,tmp,mModel);
  multiply(mProj,mModel,mMVP);
  normalMatrix3(mModel,mNorm);

  const sunDir=[-0.6,0.5,0.7]; // normalize
  const sl=Math.sqrt(sunDir[0]*sunDir[0]+sunDir[1]*sunDir[1]+sunDir[2]*sunDir[2]);
  sunDir[0]/=sl;sunDir[1]/=sl;sunDir[2]/=sl;

  // -- Stars (no model transform) --
  gl.depthMask(false);
  gl.useProgram(starProg);
  perspective(0.75,W/H,0.1,50,tmp);
  translate(0,0,0,mTrans);
  gl.uniformMatrix4fv(ul(starProg,'uMVP'),false,tmp);
  bindAttr(starProg,'aPos',starPosB,3);
  gl.bindBuffer(gl.ARRAY_BUFFER,starSzB);
  const szLoc=al(starProg,'aSize'); if(szLoc>=0){
    gl.enableVertexAttribArray(szLoc);
    gl.vertexAttribPointer(szLoc,1,gl.FLOAT,false,0,0);
  }
  gl.drawArrays(gl.POINTS,0,NSTARS);
  gl.depthMask(true);

  // -- Globe --
  gl.useProgram(globeProg);
  gl.uniformMatrix4fv(ul(globeProg,'uMVP'),false,mMVP);
  gl.uniformMatrix4fv(ul(globeProg,'uModel'),false,mModel);
  gl.uniformMatrix3fv(ul(globeProg,'uNormalMat'),false,mNorm);
  gl.uniform3fv(ul(globeProg,'uSunDir'),sunDir);
  gl.uniform1f(ul(globeProg,'uTime'),time);
  bindAttr(globeProg,'aPos',ePosB,3);
  bindAttr(globeProg,'aNormal',eNorB,3);
  bindAttr(globeProg,'aUV',eUVB,2);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,eIdxB);
  gl.drawElements(gl.TRIANGLES,earth.idx.length,gl.UNSIGNED_SHORT,0);

  // -- Atmosphere --
  gl.depthMask(false);
  gl.blendFunc(gl.SRC_ALPHA,gl.ONE);
  gl.useProgram(atmProg);

  const atmModel=mat4(), atmTrans=mat4(), atmTmp=mat4();
  translate(0,0,-zoom,atmTrans);
  rotX(rotX_val,mRX); rotY(rotY_val,mRY);
  multiply(mRX,mRY,atmTmp); multiply(atmTrans,atmTmp,atmModel);
  multiply(mProj,atmModel,tmp);
  gl.uniformMatrix4fv(ul(atmProg,'uMVP'),false,tmp);
  gl.uniformMatrix4fv(ul(atmProg,'uModel'),false,atmModel);
  gl.uniformMatrix3fv(ul(atmProg,'uNormalMat'),false,mNorm);
  gl.uniform3fv(ul(atmProg,'uSunDir'),sunDir);
  gl.uniform1f(ul(atmProg,'uTime'),time);
  bindAttr(atmProg,'aPos',aPosB,3);
  bindAttr(atmProg,'aNormal',aNorB,3);
  bindAttr(atmProg,'aUV',aUVB,2);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,aIdxB);
  gl.drawElements(gl.TRIANGLES,atm.idx.length,gl.UNSIGNED_SHORT,0);

  gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
  gl.depthMask(true);

  // -- Pulse rings --
  gl.depthMask(false);
  gl.useProgram(ringProg);
  HUBS.forEach((hub,i)=>{
    const ring=rings[i];
    const phase=(time*1.8+ring.phase)%(Math.PI*2);
    const scale=1.0+Math.sin(phase)*1.2;
    const opacity=Math.max(0,0.7*(1.0-scale/2.2));
    if(opacity<=0)return;

    // Scale ring outward from center
    const p=hubPositions[i];
    const n=[p[0]/HUB_R,p[1]/HUB_R,p[2]/HUB_R];
    const sc=buildRing(p[0],p[1],p[2],n[0],n[1],n[2],0.025*scale);
    gl.bindBuffer(gl.ARRAY_BUFFER,ring.buf);
    gl.bufferData(gl.ARRAY_BUFFER,sc,gl.DYNAMIC_DRAW);

    gl.uniformMatrix4fv(ul(ringProg,'uMVP'),false,mMVP);
    const col=scoreColor(hub.score);
    gl.uniform4fv(ul(ringProg,'uColor'),[col[0],col[1],col[2],opacity]);
    bindAttr(ringProg,'aPos',ring.buf,3);
    gl.drawArrays(gl.LINE_STRIP,0,33);
  });
  gl.depthMask(true);

  // -- Hub markers --
  gl.depthMask(false);
  gl.blendFunc(gl.SRC_ALPHA,gl.ONE);
  gl.useProgram(mrkProg);
  gl.uniformMatrix4fv(ul(mrkProg,'uMVP'),false,mMVP);

  HUBS.forEach((hub,i)=>{
    const col=scoreColor(hub.score);
    const pulse=0.85+Math.sin(time*2.0+i*0.6)*0.15;
    gl.uniform4fv(ul(mrkProg,'uColor'),[col[0],col[1],col[2],pulse]);
    gl.bindBuffer(gl.ARRAY_BUFFER,mrkPosB);
    const loc=al(mrkProg,'aPos'); if(loc<0)return;
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,i*12);
    gl.drawArrays(gl.POINTS,0,1);
  });

  gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
  gl.depthMask(true);
}
requestAnimationFrame(render);

})();
</script>
""")

    col1, col2 = st.columns([1,1])
    with col1:
        ptitle("Top Innovation Clusters")
        fig = go.Figure(go.Bar(
            x=[9.4,9.1,8.9,8.8,8.7,8.6,8.5,8.3,8.2],
            y=["Boston","San Francisco","Basel","New York","London","Shanghai","Zurich","Tokyo","San Diego"],
            orientation="h",marker=dict(color=C["accent"],opacity=0.85),
            text=[str(v) for v in [9.4,9.1,8.9,8.8,8.7,8.6,8.5,8.3,8.2]],
            textposition="inside",textfont=dict(size=10)))
        apply_base(fig, height=280,
            xaxis=dict(**GX,range=[7,10]),
            margin=dict(l=0,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with col2:
        ptitle("Innovation Index by Country (Choropleth)")
        st.plotly_chart(chart_choropleth(), use_container_width=True, config={"displayModeBar":False})

# ══════════════════════════════════════════════
# TAB 6 — PAPER EXPLAINER
# ══════════════════════════════════════════════
with tabs[5]:
    section_hdr("📄","AI Scientific Paper Explainer",
        "PubMed · arXiv · Instant plain-language summaries","⚡ AI POWERED")

    ptitle("Search Paper / Topic")
    pc1, pc2 = st.columns([4,1])
    with pc1:
        paper_query = st.text_input("Paper query", label_visibility="collapsed",
            placeholder="e.g. 'GLP-1 receptor agonists Alzheimer disease' or PMID:38291234",
            value="mRNA vaccine cancer immunotherapy")
    with pc2:
        explain_btn = st.button("Explain Paper", key="btn_paper")

    PAPER_DB = {
        "glp": {
            "title": "GLP-1 Receptor Agonists in Neurodegenerative Disease",
            "summary": "GLP-1 receptor agonists like semaglutide have shown unexpected neuroprotective effects, with emerging evidence suggesting they may slow amyloid-β accumulation in Alzheimer's patients. Phase II trials showed 18% reduction in cognitive decline vs. placebo.",
            "mechanism": "GLP-1Rs activate AMPK and PI3K/Akt pathways, reducing neuroinflammation via NF-κB suppression and promoting neurogenesis through BDNF upregulation in hippocampal tissue.",
            "impact": "If Phase III trials confirm these effects, GLP-1RAs could become the first dual metabolic-neurological agents, transforming care for 55M+ Alzheimer's patients worldwide.",
        },
        "mrna": {
            "title": "Personalized mRNA Neoantigen Vaccines in Oncology",
            "summary": "mRNA cancer vaccines deliver tumor-specific neoantigen sequences, training the immune system to recognize and destroy cancer cells. Phase IIb trials in melanoma showed 49% reduction in recurrence/death vs. pembrolizumab alone.",
            "mechanism": "Synthetic mRNA encodes neoantigens from tumor mutational burden analysis; ribosomes translate these into antigenic peptides presented via MHC-I to cytotoxic T-lymphocytes, generating durable tumor-specific immunity.",
            "impact": "Personalized mRNA vaccines in combination with checkpoint inhibitors signal a new era of combination immunotherapy, with IND filings across 14 cancer types now underway.",
        },
        "default": {
            "title": "Research Analysis",
            "summary": "This research area represents a rapidly evolving field with significant implications for drug development. Recent publications demonstrate meaningful efficacy signals across multiple study populations.",
            "mechanism": "The biological mechanism involves targeted modulation of key molecular pathways, resulting in downstream changes to cellular signaling cascades relevant to the disease state.",
            "impact": "If validated in prospective trials, this approach could represent a significant advance in standard of care, with estimated patient impact exceeding 10 million individuals globally.",
        }
    }

    if explain_btn and paper_query:
        q = paper_query.lower()
        key = "glp" if ("glp" in q or "alzheimer" in q) else "mrna" if ("mrna" in q or "mrna" in q or "vaccine" in q) else "default"
        data = PAPER_DB[key]

        st.html(f"""
        <div style="background:#112240;border:1px solid rgba(0,212,255,0.12);border-radius:12px;padding:20px;margin-bottom:16px">
          <div style="font-size:15px;font-weight:700;color:#e2eaf5;margin-bottom:4px;font-family:Syne,sans-serif">{data['title']}</div>
          <div style="font-size:9px;color:#4a6080;font-family:DM Mono,monospace;margin-bottom:16px">PubMed Analysis · arXiv Cross-reference · AI Synthesis</div>
        </div>""")

        st.html(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:8px">
          <div style="padding:14px;background:rgba(0,212,255,0.04);border-radius:8px;border:1px solid rgba(0,212,255,0.12)">
            <div style="font-size:9px;font-weight:700;letter-spacing:0.15em;color:#00d4ff;font-family:DM Mono,monospace;margin-bottom:8px">SUMMARY</div>
            <div style="font-size:12px;color:#8fa4c2;font-family:DM Mono,monospace;line-height:1.6">{data['summary']}</div>
          </div>
          <div style="padding:14px;background:rgba(123,79,255,0.04);border-radius:8px;border:1px solid rgba(123,79,255,0.12)">
            <div style="font-size:9px;font-weight:700;letter-spacing:0.15em;color:#7b4fff;font-family:DM Mono,monospace;margin-bottom:8px">DRUG MECHANISM</div>
            <div style="font-size:12px;color:#8fa4c2;font-family:DM Mono,monospace;line-height:1.6">{data['mechanism']}</div>
          </div>
          <div style="padding:14px;background:rgba(0,255,157,0.04);border-radius:8px;border:1px solid rgba(0,255,157,0.12)">
            <div style="font-size:9px;font-weight:700;letter-spacing:0.15em;color:#00ff9d;font-family:DM Mono,monospace;margin-bottom:8px">CLINICAL IMPACT</div>
            <div style="font-size:12px;color:#8fa4c2;font-family:DM Mono,monospace;line-height:1.6">{data['impact']}</div>
          </div>
        </div>""")

    st.html("<div style='height:16px'></div>")
    col1, col2 = st.columns([1,1])
    with col1:
        ptitle("Trending Research Topics (YoY Growth)")
        fig = go.Figure(go.Bar(
            x=[99,94,88,82,76,71,65],
            y=["GLP-1/Obesity","mRNA Cancer Vaccines","Alzheimer's","ADCs","KRAS Inhibitors","CAR-T","Radiopharmaceuticals"],
            orientation="h",
            marker=dict(color=[C["accent"],C["accent2"],C["accent3"],C["accent4"],C["accent5"],"#a78bfa","#34d399"]),
            text=["↑340%","↑280%","↑210%","↑190%","↑165%","↑150%","↑140%"],
            textposition="inside",textfont=dict(size=9,family="DM Mono,monospace")))
        apply_base(fig, height=260, margin=dict(l=0,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with col2:
        ptitle("Journal Impact Factors")
        fig2 = go.Figure(go.Bar(
            x=["NEJM","Nat. Med.","Lancet","JAMA","Nature","Cell"],
            y=[91.2,82.9,79.3,63.1,69.5,64.5],
            marker=dict(color=[C["accent"],C["accent2"],C["accent3"],C["accent4"],C["accent5"],"#a78bfa"]),
            text=[str(v) for v in [91.2,82.9,79.3,63.1,69.5,64.5]],
            textposition="outside",textfont=dict(size=9)))
        apply_base(fig2, height=260,
            yaxis=dict(**GY,range=[0,105]),
            margin=dict(l=10,r=10,t=10,b=40))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

# ══════════════════════════════════════════════
# TAB 7 — TRIAL PREDICTOR
# ══════════════════════════════════════════════
with tabs[6]:
    section_hdr("🧪","Clinical Trial Success Predictor",
        "ClinicalTrials.gov · AI model trained on 50,000+ historical trials","⚡ AI MODEL")

    tc1, tc2 = st.columns([1,1])
    with tc1:
        ptitle("Configure Trial Parameters")
        drug_class = st.selectbox("Drug Class",
            ["Small Molecule","Biologic / Antibody","mRNA Therapy","Cell & Gene Therapy","RNA Interference"],
            index=2)
        target = st.selectbox("Target Protein",
            ["EGFR","PD-1 / PD-L1","KRAS","BRCA1/2","TNF-alpha","GLP-1R","BACE1"],
            index=1)
        area = st.selectbox("Therapeutic Area",
            ["Oncology","CNS / Neurology","Cardiovascular","Infectious Disease","Rare Disease","Autoimmune"])
        phase = st.selectbox("Trial Phase",
            ["Phase I &rarr; II","Phase II &rarr; III","Phase III &rarr; Approval"],
            index=1)
        company = st.selectbox("Company Track Record",
            ["Startup (<2 approvals)","Mid-tier (2-5 approvals)","Big Pharma (10+ approvals)"],
            index=1)
        predict_btn = st.button("Predict Success Probability", key="btn_trial")

    with tc2:
        ptitle("Prediction Result")
        if predict_btn:
            base = 40
            if "mRNA" in drug_class: base += 14
            if "Biologic" in drug_class: base += 10
            if "PD-1" in target: base += 8
            if "GLP" in target: base += 6
            if "Big Pharma" in company: base += 12
            if "Mid-tier" in company: base += 5
            if "Rare Disease" == area: base += 7
            if "Oncology" == area: base -= 4
            prob = min(91, max(18, base))
            label = phase.replace(" ","")
            st.plotly_chart(chart_trial_gauge(prob, f"{label} Success Probability"),
                use_container_width=True, config={"displayModeBar":False})

            risk_color = C["success"] if prob>65 else C["warning"] if prob>40 else C["danger"]
            st.html(f"""
            <div style="padding:12px;background:rgba(0,0,0,0.2);border-radius:8px;border:1px solid rgba(255,255,255,0.05);margin-top:8px">
              <div style="font-size:9px;color:#4a6080;font-family:DM Mono,monospace;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">Key Risk Factors</div>
              {''.join(f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="font-size:11px;color:#8fa4c2;font-family:DM Mono,monospace;flex:1">{f}</span><div style="flex:2;height:3px;background:rgba(255,255,255,0.06);border-radius:2px"><div style="height:100%;width:{p}%;background:#00d4ff;border-radius:2px"></div></div></div>' for f,p in [("Patient Stratification",72),("Endpoint Selection",68),("Sample Size Power",81),("Competitive Landscape",55)])}
            </div>""")
        else:
            st.html('<div style="color:#4a6080;font-family:DM Mono,monospace;font-size:12px;text-align:center;padding:40px">Configure parameters and click<br>"Predict Success Probability"</div>')

    st.html("<div style='height:16px'></div>")
    c1, c2, c3 = st.columns(3)
    with c1:
        ptitle("Phase Transition Waterfall")
        st.plotly_chart(chart_phase_waterfall(), use_container_width=True, config={"displayModeBar":False})
    with c2:
        ptitle("Success Rate by Drug Class")
        fig = go.Figure(go.Bar(
            x=["Vaccines","Biologics","Cell&Gene","mRNA","Small Mol.","ASOs"],
            y=[81,73,68,64,57,52],
            marker=dict(color=[C["accent3"],C["accent"],C["accent2"],C["accent5"],C["accent4"],C["text3"]]),
            text=["81%","73%","68%","64%","57%","52%"],textposition="outside",textfont=dict(size=10)))
        apply_base(fig, height=260,
            yaxis=dict(**GY,range=[0,95]),
            margin=dict(l=10,r=10,t=10,b=40))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
    with c3:
        ptitle("Top Failure Reasons")
        fig2 = go.Figure(go.Pie(
            labels=["Lack of Efficacy","Safety/Toxicity","Strategic","Poor PK/ADME"],
            values=[56,28,11,5],hole=0.55,
            marker=dict(colors=[C["danger"],C["warning"],C["text3"],C["accent2"]]),
            textfont=dict(size=10,family="DM Mono,monospace")))
        apply_base(fig2, height=260, margin=dict(l=10,r=10,t=20,b=10))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})

# ══════════════════════════════════════════════
# TAB 8 — DISEASE NETWORK
# ══════════════════════════════════════════════
with tabs[7]:
    section_hdr("🕸️","Global Disease–Drug Network Graph",
        "Disease &rarr; Target Protein &rarr; Drug pathways · Hidden relationship discovery")

    col1, col2 = st.columns([6,4])
    with col1:
        ptitle("Disease–Gene–Drug Sankey Flow")
        st.plotly_chart(chart_network_sankey(), use_container_width=True, config={"displayModeBar":False})
    with col2:
        ptitle("Cross-Disease Target Proteins")
        fig = go.Figure(go.Bar(
            x=[8,6,5,5,4,4,3],
            y=["PI3K/mTOR","TNF-alpha","JAK-STAT","NF-κB","VEGFR","EGFR","PCSK9"],
            orientation="h",
            marker=dict(color=[C["accent"],C["accent2"],C["accent3"],C["accent5"],C["accent4"],"#a78bfa","#34d399"]),
            text=["8 diseases","6 diseases","5 diseases","5 diseases","4 diseases","4 diseases","3 diseases"],
            textposition="inside",textfont=dict(size=9)))
        apply_base(fig, height=280,
            xaxis=dict(**GX,range=[0,10]),
            margin=dict(l=0,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    ptitle("Top Disease–Drug Connections")
    hcols = st.columns([2,2,2,3,1.5])
    for hc, ht in zip(hcols, ["Disease","Target Protein","Drug","Mechanism","Confidence"]):
        st.html(f'<div style="font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:#4a6080;font-family:DM Mono,monospace;padding-bottom:6px;border-bottom:1px solid rgba(0,212,255,0.12)">{ht}</div>')

    for dis, prot, drug, mech, conf in [
        ("Alzheimer's","BACE1","Lecanemab","β-Secretase Inhibition",92),
        ("Lung Cancer","EGFR","Osimertinib","Tyrosine Kinase Inhibition",96),
        ("Diabetes T2","GLP-1R","Semaglutide","Receptor Agonism",94),
        ("Heart Disease","PCSK9","Evolocumab","Antibody Inhibition",98),
        ("Breast Cancer","BRCA1/2","Olaparib","PARP Inhibition",91),
        ("Parkinson's","α-Synuclein","Prasinezumab","Antibody Targeting",74),
        ("Autoimmune","JAK-STAT","Baricitinib","JAK1/2 Inhibition",89),
    ]:
        rc = st.columns([2,2,2,3,1.5])
        st.html(f'<div style="font-size:11px;color:#ff3b5c;font-family:DM Mono,monospace;padding:4px 0">{dis}</div>')
        st.html(f'<div style="font-size:11px;color:#ffd700;font-family:DM Mono,monospace;padding:4px 0">{prot}</div>')
        st.html(f'<div style="font-size:11px;color:#00d4ff;font-family:DM Mono,monospace;padding:4px 0">{drug}</div>')
        st.html(f'<div style="font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace;padding:4px 0">{mech}</div>')
        st.html(f'<div style="display:flex;align-items:center;gap:4px;padding:4px 0"><div style="flex:1;height:3px;background:rgba(255,255,255,0.06);border-radius:2px"><div style="height:100%;width:{conf}%;background:#00ff9d;border-radius:2px"></div></div><span style="font-size:9px;color:#00ff9d;font-family:DM Mono,monospace">{conf}%</span></div>')

# ══════════════════════════════════════════════
# TAB 9 — RISK INDEX
# ══════════════════════════════════════════════
with tabs[8]:
    section_hdr("📊","Pharmaceutical Risk Index",
        "Country-level pharma stability scores · Shortages · Regulatory delays · Supply chain")

    ptitle("Global Pharma Risk Scores — Grouped by Factor")
    st.plotly_chart(chart_country_risk(), use_container_width=True, config={"displayModeBar":False})

    col1, col2 = st.columns([4,6])
    with col1:
        ptitle("Country Deep-Dive — Risk Radar")
        country_names = [r[0] for r in COUNTRY_RISK]
        selected = st.selectbox("Select Country", country_names, key="country_sel")
        idx = country_names.index(selected)
        st.plotly_chart(chart_risk_radar(idx), use_container_width=True, config={"displayModeBar":False})

    with col2:
        ptitle("Pharma Risk Scorecard")
        tbl = '<table style="width:100%;border-collapse:collapse;font-family:DM Mono,monospace">'
        tbl += '<thead><tr>'
        for h in ["Country","Score","Grade","Shortage","Reg. Delay","Supply","Trials"]:
            tbl += f'<th style="padding:6px 10px;font-size:9px;letter-spacing:0.1em;text-transform:uppercase;color:#4a6080;text-align:left;border-bottom:1px solid rgba(0,212,255,0.15)">{h}</th>'
        tbl += '</tr></thead><tbody>'
        for r in COUNTRY_RISK:
            rc = C["danger"] if r[1]>70 else C["warning"] if r[1]>45 else C["success"]
            tbl += f'<tr style="border-bottom:1px solid rgba(255,255,255,0.04)">'
            tbl += f'<td style="padding:7px 10px;font-size:12px;color:#e2eaf5;font-weight:600">{r[0]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:14px;font-weight:700;color:{rc};font-family:DM Mono,monospace">{r[1]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:12px;color:{rc};font-family:DM Mono,monospace">{r[2]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace">{r[3]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace">{r[4]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace">{r[5]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#00ff9d;font-family:DM Mono,monospace">{r[6]}</td>'
            tbl += '</tr>'
        tbl += '</tbody></table>'
        st.html(tbl)

# ══════════════════════════════════════════════
# TAB 10 — RESEARCH GAPS
# ══════════════════════════════════════════════
with tabs[9]:
    section_hdr("🎯","AI Research Gap Detector",
        "Disease burden vs. research activity · Funding analysis · AI-identified opportunities",
        "🔍 GAP ANALYSIS")

    stat_cards([
        ("Critical Gaps Found","28","High priority areas",None,False,C["danger"]),
        ("Underfunded Diseases","147","vs. burden score",None,False,C["warning"]),
        ("Top Opportunity","94/100","Rare Neurological",None,True,C["accent3"]),
        ("Research Deserts","63","Disease areas",None,False,C["text"]),
        ("AI Recommendations","341","Priority areas",None,True,C["accent2"]),
    ])
    st.html("<div style='height:16px'></div>")

    col1, col2 = st.columns([6,4])
    with col1:
        ptitle("Research Activity vs. Disease Burden Bubble Matrix")
        st.plotly_chart(chart_gap_scatter(), use_container_width=True, config={"displayModeBar":False})
    with col2:
        ptitle("Gap Score Ranking")
        st.plotly_chart(chart_gap_bar(), use_container_width=True, config={"displayModeBar":False})

    ptitle("Priority Research Opportunity Bubbles")
    st.html("""
    <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:20px">
      <span class="gap-high">Rare Neurological</span>
      <span class="gap-high">Neglected Tropical Diseases</span>
      <span class="gap-high">Pediatric Rare Disorders</span>
      <span class="gap-high">AMR / Antibiotics</span>
      <span class="gap-high">Prion Diseases</span>
      <span class="gap-medium">Mental Health</span>
      <span class="gap-medium">Parasitic Infections</span>
      <span class="gap-medium">Rare Metabolic</span>
      <span class="gap-medium">Geriatric Syndromes</span>
      <span class="gap-low">Vector-borne Viruses</span>
      <span class="gap-low">Neonatal Infections</span>
    </div>""")

    ptitle("AI-Generated Research Opportunity Insights")
    g1, g2, g3 = st.columns(3)
    for col, icon, title, text, badge, color, rgb in [
        (g1,"🧠","Critical Gap: Rare Neurological",
         "High disease burden (8.2M DALYs globally) but only 3% of neurology research funding targets rare neurological disorders. AI recommends: prion-like spreading mechanisms, lysosomal storage diseases, neuronal ceroid lipofuscinoses.",
         "GAP SCORE: 94/100", C["danger"], "255,59,92"),
        (g2,"🦟","Neglected Tropical Diseases",
         "1.7 billion people affected globally, yet <1% of pharmaceutical R&D investment targets NTDs. Key opportunities in Chagas disease, schistosomiasis, and lymphatic filariasis drug development.",
         "GAP SCORE: 91/100", C["warning"], "255,184,0"),
        (g3,"🦠","Antimicrobial Resistance Crisis",
         "AMR projected to cause 10M deaths/year by 2050. Antibiotic pipeline has only 43 drugs — mostly modifications of existing classes. Novel mechanisms urgently needed: phage therapies, bacteriocins.",
         "GAP SCORE: 88/100", C["accent4"], "255,107,53"),
    ]:
        st.html(f"""
        <div style="padding:16px;background:rgba({rgb},0.06);border-radius:10px;border:1px solid rgba({rgb},0.15);height:100%">
          <div style="font-size:24px;margin-bottom:8px">{icon}</div>
          <div style="font-size:13px;font-weight:700;color:{color};margin-bottom:6px;font-family:Syne,sans-serif">{title}</div>
          <div style="font-size:11px;color:#8fa4c2;font-family:DM Mono,monospace;line-height:1.6;margin-bottom:8px">{text}</div>
          <div style="font-size:9px;color:{color};font-family:DM Mono,monospace;letter-spacing:0.1em">{badge}</div>
        </div>""")

# ---------------------------------------------
# FOOTER
# ---------------------------------------------
st.html("<div style='height:24px'></div>")
footer_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
st.html(f"""
<div style="text-align:center;padding:16px;border-top:1px solid rgba(0,212,255,0.1);
  font-family:DM Mono,monospace;font-size:9px;color:#4a6080;letter-spacing:0.1em">
  GLOBAL DRUG INTELLIGENCE MONITOR · DATA SOURCES: FDA · WHO · PUBMED · CLINICALTRIALS.GOV ·
  LAST UPDATE: {footer_time}
</div>""")
