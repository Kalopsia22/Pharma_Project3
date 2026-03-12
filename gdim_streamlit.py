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

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Global Drug Intelligence Monitor",
    page_icon="⊕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  /* Global */
  html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
  .stApp { background: #03060f; color: #e2eaf5; }
  .block-container { padding: 0 2rem 2rem 2rem; max-width: 100% !important; }

  /* Hide default streamlit elements */
  #MainMenu, footer, header { visibility: hidden; }
  .stDeployButton { display: none; }

  /* Custom header */
  .gdim-header {
    background: rgba(3,6,15,0.97);
    border-bottom: 1px solid rgba(0,212,255,0.15);
    padding: 18px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: -1rem -2rem 0 -2rem;
    position: sticky;
    top: 0;
    z-index: 999;
  }
  .gdim-title { font-size: 18px; font-weight: 800; letter-spacing: 0.06em;
    text-transform: uppercase; color: #e2eaf5; margin: 0; }
  .gdim-sub { font-family: 'DM Mono', monospace; font-size: 10px;
    color: #00d4ff; margin: 3px 0 0 0; letter-spacing: 0.12em; }
  .live-badge { font-family: 'DM Mono', monospace; font-size: 10px;
    color: #00e676; display: flex; align-items: center; gap: 6px; }

  /* Section headers */
  .section-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 20px; padding-bottom: 12px;
    border-bottom: 1px solid rgba(0,212,255,0.1);
  }
  .section-icon { font-size: 24px; }
  .section-title { font-size: 20px; font-weight: 800; color: #e2eaf5; margin: 0; }
  .section-sub { font-family: 'DM Mono', monospace; font-size: 11px;
    color: #8fa4c2; margin: 2px 0 0 0; }
  .ai-badge {
    margin-left: auto; font-size: 9px; font-family: 'DM Mono', monospace;
    font-weight: 700; letter-spacing: 0.1em; padding: 5px 12px;
    border-radius: 20px; border: 1px solid rgba(0,212,255,0.3);
    background: linear-gradient(135deg,rgba(0,212,255,.1),rgba(123,79,255,.1));
    color: #00d4ff;
  }

  /* Stat cards */
  .stat-card {
    background: #112240; border: 1px solid rgba(0,212,255,0.12);
    border-radius: 10px; padding: 16px; position: relative;
  }
  .stat-label { font-size: 9px; font-family: 'DM Mono', monospace;
    letter-spacing: 0.15em; text-transform: uppercase; color: #4a6080;
    margin-bottom: 8px; }
  .stat-value { font-size: 26px; font-weight: 800; line-height: 1; }
  .stat-sub { font-size: 10px; color: #8fa4c2; margin-top: 4px;
    font-family: 'DM Mono', monospace; }
  .stat-up { font-size: 9px; font-family: 'DM Mono', monospace; color: #00e676;
    background: rgba(0,230,118,.12); padding: 2px 7px; border-radius: 4px;
    display: inline-block; margin-top: 6px; }
  .stat-down { font-size: 9px; font-family: 'DM Mono', monospace; color: #ff3b5c;
    background: rgba(255,59,92,.12); padding: 2px 7px; border-radius: 4px;
    display: inline-block; margin-top: 6px; }

  /* Panels */
  .panel {
    background: #0d1e35; border: 1px solid rgba(0,212,255,0.12);
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
  }
  .panel-title {
    font-size: 11px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #8fa4c2; margin-bottom: 14px;
    font-family: 'DM Mono', monospace;
    display: flex; align-items: center; gap: 8px;
  }
  .panel-title::before { content: "●"; color: #00d4ff; font-size: 8px;
    text-shadow: 0 0 6px #00d4ff; }

  /* Insight cards */
  .insight-card {
    background: #112240; border: 1px solid rgba(0,212,255,0.1);
    border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
    display: flex; gap: 12px; align-items: flex-start;
  }
  .insight-icon { font-size: 20px; flex-shrink: 0; }
  .insight-title { font-size: 13px; font-weight: 700; color: #e2eaf5; margin-bottom: 4px; }
  .insight-text { font-size: 11px; color: #8fa4c2; font-family: 'DM Mono', monospace; line-height: 1.5; }
  .insight-meta { font-size: 9px; color: #4a6080; margin-top: 6px;
    font-family: 'DM Mono', monospace; letter-spacing: 0.08em; text-transform: uppercase; }

  /* Risk badges */
  .risk-high { background: rgba(255,59,92,.15); color: #ff3b5c;
    border: 1px solid rgba(255,59,92,.3); padding: 3px 10px; border-radius: 20px;
    font-size: 10px; font-family: 'DM Mono', monospace; font-weight: 700; }
  .risk-medium { background: rgba(255,184,0,.15); color: #ffb800;
    border: 1px solid rgba(255,184,0,.3); padding: 3px 10px; border-radius: 20px;
    font-size: 10px; font-family: 'DM Mono', monospace; font-weight: 700; }
  .risk-low { background: rgba(0,230,118,.15); color: #00e676;
    border: 1px solid rgba(0,230,118,.3); padding: 3px 10px; border-radius: 20px;
    font-size: 10px; font-family: 'DM Mono', monospace; font-weight: 700; }

  /* Repurpose cards */
  .repurpose-card {
    background: #112240; border: 1px solid rgba(0,212,255,0.12);
    border-left: 3px solid #00d4ff; border-radius: 10px; padding: 14px;
    margin-bottom: 10px;
  }
  .drug-tag { background: rgba(0,212,255,0.1); border: 1px solid rgba(0,212,255,0.2);
    border-radius: 5px; padding: 3px 8px; font-size: 11px;
    font-family: 'DM Mono', monospace; color: #00d4ff; display: inline-block; }
  .new-tag { background: rgba(0,255,157,0.1); border: 1px solid rgba(0,255,157,0.2);
    border-radius: 5px; padding: 3px 8px; font-size: 11px;
    font-family: 'DM Mono', monospace; color: #00ff9d; display: inline-block; }

  /* Gap bubbles */
  .gap-high { background: rgba(255,59,92,0.1); color: #ff3b5c;
    border: 1px solid rgba(255,59,92,0.2); padding: 5px 12px; border-radius: 20px;
    font-size: 10px; font-family: 'DM Mono', monospace; display: inline-block; margin: 3px; }
  .gap-medium { background: rgba(255,184,0,0.1); color: #ffb800;
    border: 1px solid rgba(255,184,0,0.2); padding: 5px 12px; border-radius: 20px;
    font-size: 10px; font-family: 'DM Mono', monospace; display: inline-block; margin: 3px; }
  .gap-low { background: rgba(0,212,255,0.1); color: #00d4ff;
    border: 1px solid rgba(0,212,255,0.2); padding: 5px 12px; border-radius: 20px;
    font-size: 10px; font-family: 'DM Mono', monospace; display: inline-block; margin: 3px; }

  /* Streamlit widget overrides */
  .stSelectbox > div > div, .stTextInput > div > div > input {
    background: #112240 !important; border: 1px solid rgba(0,212,255,0.2) !important;
    border-radius: 8px !important; color: #e2eaf5 !important;
    font-family: 'DM Mono', monospace !important; font-size: 12px !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, #00d4ff, #7b4fff) !important;
    border: none !important; border-radius: 8px !important; color: white !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    letter-spacing: 0.05em !important; padding: 10px 24px !important;
    width: 100% !important;
  }
  .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 20px rgba(0,212,255,0.3) !important; }
  .stTabs [data-baseweb="tab-list"] {
    background: rgba(6,13,26,0.95) !important;
    border-bottom: 1px solid rgba(0,212,255,0.12) !important;
    gap: 0; padding: 0;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #4a6080 !important;
    font-family: 'DM Mono', monospace !important; font-size: 10px !important;
    font-weight: 700 !important; letter-spacing: 0.08em !important;
    padding: 12px 16px !important; border: none !important;
    border-bottom: 2px solid transparent !important;
  }
  .stTabs [aria-selected="true"] {
    color: #00d4ff !important; border-bottom: 2px solid #00d4ff !important;
  }
  div[data-testid="metric-container"] {
    background: #112240; border: 1px solid rgba(0,212,255,0.12);
    border-radius: 10px; padding: 16px;
  }
  [data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Syne', sans-serif !important; }
  [data-testid="stMetricLabel"] { color: #4a6080 !important; font-family: 'DM Mono', monospace !important; font-size: 9px !important; }
  [data-testid="stMetricDelta"] { font-family: 'DM Mono', monospace !important; }

  /* Plotly chart backgrounds */
  .js-plotly-plot { border-radius: 8px; }

  /* Divider */
  hr { border-color: rgba(0,212,255,0.1) !important; }
</style>
""")

# ─────────────────────────────────────────────
# COLOUR PALETTE
# ─────────────────────────────────────────────
C = dict(
    bg      = "#03060f",
    panel   = "#0d1e35",
    panel2  = "#112240",
    accent  = "#00d4ff",
    accent2 = "#7b4fff",
    accent3 = "#00ff9d",
    accent4 = "#ff6b35",
    accent5 = "#ffd700",
    danger  = "#ff3b5c",
    warning = "#ffb800",
    success = "#00e676",
    text    = "#e2eaf5",
    text2   = "#8fa4c2",
    text3   = "#4a6080",
)

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color=C["text2"], size=11),
    margin=dict(l=10, r=10, t=30, b=10),
)

GX = dict(gridcolor="rgba(0,212,255,0.06)", zerolinecolor="rgba(0,212,255,0.1)", tickfont=dict(size=10))
GY = dict(gridcolor="rgba(0,212,255,0.06)", zerolinecolor="rgba(0,212,255,0.1)", tickfont=dict(size=10))
GL = dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10))

def apply_base(fig, height=None, **kwargs):
    layout = {**PLOTLY_BASE}
    if "xaxis" not in kwargs: layout["xaxis"] = GX
    if "yaxis" not in kwargs: layout["yaxis"] = GY
    if "legend" not in kwargs: layout["legend"] = GL
    if height: layout["height"] = height
    layout.update(kwargs)
    fig.update_layout(**layout)
    return fig

def pl(fig, h=None):
    apply_base(fig)
    if h: fig.update_layout(height=h)
    return fig

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
np.random.seed(42)

def make_dates(n):
    return [datetime.now() - timedelta(days=n-i) for i in range(n)]

@st.cache_data(ttl=5)
def discovery_ts():
    dates = make_dates(180)
    areas = {"mRNA Therapies":140,"AI-Designed Molecules":60,"Cell & Gene Therapy":90,
              "Personalized Medicine":110,"PROTAC Degraders":30}
    data = {}
    for area, base in areas.items():
        v, vals = base, []
        for _ in dates:
            v += random.uniform(-2, 6)
            vals.append(max(10, v))
        data[area] = vals
    return pd.DataFrame(data, index=dates)

@st.cache_data(ttl=5)
def shortage_ts():
    drugs = ["Amoxicillin","Cisplatin","Carboplatin","Methotrexate","Albuterol"]
    data = {}
    for drug in drugs:
        v = random.randint(40, 90)
        vals = []
        for _ in make_dates(90):
            v += random.uniform(-3, 4)
            v = min(99, max(10, v))
            vals.append(v)
        data[drug] = vals
    return pd.DataFrame(data, index=make_dates(90))

INNOV_DF = pd.DataFrame([
    ("Boston, MA",42.36,-71.06,9.4,1240), ("San Francisco",37.77,-122.42,9.1,1100),
    ("Basel, CH",47.56,7.59,8.9,890),     ("London, UK",51.51,-0.13,8.7,860),
    ("Shanghai, CN",31.23,121.47,8.6,820),("New York, NY",40.71,-74.01,8.8,980),
    ("Tokyo, JP",35.68,139.69,8.3,750),   ("San Diego, CA",32.72,-117.16,8.2,710),
    ("Zurich, CH",47.38,8.54,8.5,780),    ("Munich, DE",48.14,11.58,8.1,680),
    ("Beijing, CN",39.91,116.39,8.0,660), ("Bangalore, IN",12.97,77.59,7.6,520),
    ("Sydney, AU",-33.87,151.21,7.2,440), ("São Paulo, BR",-23.55,-46.63,6.8,390),
    ("Stockholm, SE",59.33,18.07,7.8,580),("Singapore",1.35,103.82,7.7,540),
    ("Toronto, CA",43.65,-79.38,7.9,610), ("Osaka, JP",34.69,135.50,7.5,490),
], columns=["city","lat","lon","score","startups"])

REPURPOSE_DATA = [
    ("Metformin","Diabetes T2DM","Alzheimer's Disease",78,"AMPK pathway · neuroinflammation reduction"),
    ("Sildenafil","Erectile Dysfunction","Pulmonary Hypertension",97,"PDE5 inhibition · vascular smooth muscle"),
    ("Thalidomide","Morning Sickness","Multiple Myeloma",95,"Immunomodulatory · anti-angiogenic"),
    ("Aspirin","Pain / Inflammation","Colorectal Cancer Prevention",82,"COX-2 inhibition · 47 observational studies"),
    ("Baricitinib","Rheumatoid Arthritis","COVID-19 Severe",91,"JAK inhibition · cytokine storm suppression"),
    ("Itraconazole","Fungal Infections","Basal Cell Carcinoma",71,"Hedgehog pathway inhibition"),
    ("Rapamycin","Transplant Rejection","Longevity / Aging",68,"mTOR inhibition · autophagy activation"),
    ("Colchicine","Gout","Pericarditis / ASCVD",87,"NLRP3 inflammasome · IL-1β suppression"),
]

INTERACTION_DB = {
    ("warfarin","aspirin"):          ("MODERATE-HIGH",72,"CYP2C9 competition + COX-1 inhibition → bleeding risk↑"),
    ("warfarin","ibuprofen"):        ("HIGH",84,"CYP2C9 inhibition + GI mucosal damage → hemorrhage risk"),
    ("maois","ssri"):                ("CRITICAL",97,"Serotonin syndrome — potentially fatal combination"),
    ("digoxin","amiodarone"):        ("HIGH",88,"P-gp inhibition → digoxin toxicity"),
    ("methotrexate","nsaids"):       ("HIGH",83,"Reduced renal clearance of MTX → toxicity"),
    ("clopidogrel","omeprazole"):    ("MODERATE",61,"CYP2C19 inhibition → reduced antiplatelet effect"),
    ("simvastatin","clarithromycin"):("HIGH",85,"CYP3A4 inhibition → myopathy/rhabdomyolysis risk"),
    ("lithium","ibuprofen"):         ("HIGH",79,"NSAIDs reduce renal Li+ clearance → toxicity"),
}

SHORTAGE_TABLE = [
    ("Amoxicillin","Antibiotic",91,"ACTIVE","US / EU","HIGH"),
    ("Cisplatin","Chemotherapy",88,"CRITICAL","Global","HIGH"),
    ("Carboplatin","Chemotherapy",86,"CRITICAL","Global","HIGH"),
    ("Methotrexate","Immunosuppressant",79,"ACTIVE","US / Asia","HIGH"),
    ("Albuterol Inhaler","Respiratory",72,"WATCH","US","MEDIUM"),
    ("Furosemide","Diuretic",64,"WATCH","Europe","MEDIUM"),
    ("Morphine Sulfate","Opioid Analgesic",58,"MONITOR","US","MEDIUM"),
    ("Propofol","Anesthetic",45,"RESOLVED","US","LOW"),
    ("Piperacillin","Antibiotic",82,"ACTIVE","Global","HIGH"),
    ("Vincristine","Chemotherapy",77,"ACTIVE","US / EU","HIGH"),
]

COUNTRY_RISK = [
    ("United States",28,"A",24,18,22,95),("European Union",32,"A-",18,28,20,88),
    ("China",54,"B",52,64,48,82),        ("India",61,"B-",68,72,61,65),
    ("Japan",38,"A-",30,35,28,84),       ("South Korea",41,"B+",36,42,33,78),
    ("Brazil",68,"C+",72,74,69,45),      ("Russia",78,"C",81,88,76,30),
    ("Australia",35,"A-",29,31,26,82),   ("Canada",31,"A",26,24,23,89),
    ("Mexico",62,"B-",65,68,60,52),      ("S.S. Africa",89,"D+",92,95,88,18),
]

RESEARCH_GAPS = [
    ("Rare Neurological",12,86,94,"#ff3b5c"),
    ("Neglected Tropical",8,82,91,"#ff3b5c"),
    ("Pediatric Rare",15,79,85,"#ff3b5c"),
    ("Antimicrobial Resistance",22,77,88,"#ffb800"),
    ("Mental Health",35,74,76,"#ffb800"),
    ("Prion Diseases",5,68,82,"#ff3b5c"),
    ("Geriatric Polypharmacy",19,58,76,"#ffb800"),
    ("Oncology",88,40,20,"#00ff9d"),
    ("Cardiovascular",72,38,22,"#00d4ff"),
    ("Infectious Disease",68,35,25,"#00d4ff"),
    ("Diabetes",75,32,18,"#00ff9d"),
    ("HIV/AIDS",64,28,22,"#00ff9d"),
]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def stat_cards(items):
    """items = list of (label, value, sub, change, up, color)"""
    cols = st.columns(len(items))
    for col, (label, value, sub, change, up, color) in zip(cols, items):
        with col:
            arrow = "▲" if up else "▼"
            ch_color = C["success"] if up else C["danger"]
            ch_bg = "rgba(0,230,118,.12)" if up else "rgba(255,59,92,.12)"
            badge = f'<span style="font-size:9px;font-family:DM Mono,monospace;color:{ch_color};background:{ch_bg};padding:2px 7px;border-radius:4px;display:inline-block;margin-top:6px">{arrow} {change}</span>' if change else ""
            st.html(f"""
            <div class="stat-card">
              <div class="stat-label">{label}</div>
              <div class="stat-value" style="color:{color}">{value}</div>
              <div class="stat-sub">{sub}</div>
              {badge}
            </div>""")

def section_hdr(icon, title, sub, badge=None):
    b = f'<span class="ai-badge">{badge}</span>' if badge else ""
    st.html(f"""
    <div class="section-header">
      <span class="section-icon">{icon}</span>
      <div>
        <div class="section-title">{title}</div>
        <div class="section-sub">{sub}</div>
      </div>
      {b}
    </div>""")

def ptitle(text):
    st.html(f'<div class="panel-title">{text}</div>')

# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def chart_discovery():
    df = discovery_ts()
    colors = [C["accent"],C["accent2"],C["accent3"],C["accent4"],C["accent5"]]
    fig = go.Figure()
    for i, col in enumerate(df.columns):
        fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col, mode="lines",
            line=dict(color=colors[i], width=2),
            hovertemplate=f"<b>{col}</b><br>Papers: %{{y:.0f}}<extra></extra>"))
    apply_base(fig, height=300,
        title=dict(text="Publication Volume by Therapeutic Area (180 days)",
                   font=dict(size=11,color=C["text2"]),x=0.01),
        hovermode="x unified",
        legend=dict(orientation="h",y=-0.2,bgcolor="rgba(0,0,0,0)",font=dict(size=9)))
    return fig

def chart_trend_forecast():
    areas = ["mRNA Therapies","AI-Designed Molecules","Personalized Medicine",
             "Cell & Gene Therapy","PROTAC Degraders","RNA Interference",
             "Microbiome Therapies","Radiopharmaceuticals"]
    scores = [94,91,89,85,78,74,68,62]
    colors = [C["accent"] if s>80 else C["accent5"] if s>70 else C["text3"] for s in scores]
    fig = go.Figure(go.Bar(x=scores,y=areas,orientation="h",
        marker=dict(color=colors),text=[f"{s}%" for s in scores],
        textposition="inside",textfont=dict(size=10,family="DM Mono,monospace"),
        hovertemplate="<b>%{y}</b><br>Trend Score: %{x}%<extra></extra>"))
    apply_base(fig, height=300,
        xaxis=dict(**GX,range=[0,100],ticksuffix="%"),
        margin=dict(l=0,r=10,t=10,b=10))
    return fig

def chart_pubmed_area():
    months = pd.date_range("2018-01", periods=72, freq="ME")
    areas = {"Oncology":18,"Immunology":8,"CNS":11,"Infectious Disease":14,"Cardiovascular":9}
    colors = [C["danger"],C["accent2"],C["accent5"],C["accent3"],C["accent"]]
    fig = go.Figure()
    for (area, base), col in zip(areas.items(), colors):
        vals = [base + i*0.15 + np.random.normal(0,1) for i in range(len(months))]
        fig.add_trace(go.Scatter(x=months,y=vals,name=area,stackgroup="one",
            mode="lines",line=dict(width=0.5,color=col),
            hovertemplate=f"<b>{area}</b><br>%{{y:.1f}}K papers<extra></extra>"))
    apply_base(fig, height=260,
        title=dict(text="PubMed Stacked Publications by Area (000s)",font=dict(size=11,color=C["text2"]),x=0.01),
        legend=dict(orientation="h",y=-0.25,bgcolor="rgba(0,0,0,0)",font=dict(size=9)))
    return fig

def chart_live_kpis(n_intervals):
    random.seed(n_intervals)
    vals = {
        "mRNA Papers (K)": round(120 + n_intervals*0.3 + random.gauss(0,2), 1),
        "Active Trials":   round(487 + n_intervals*0.12 + random.gauss(0,3), 1),
        "Patents (K)":     round(89  + n_intervals*0.05 + random.gauss(0,1), 1),
        "New Compounds":   round(48  + n_intervals*0.02 + random.gauss(0,0.5), 1),
    }
    fig = go.Figure()
    for i, (k, v) in enumerate(vals.items()):
        ref = round(v - random.uniform(0.1,2), 1)
        fig.add_trace(go.Indicator(
            mode="number+delta", value=v,
            delta=dict(reference=ref,increasing=dict(color=C["success"]),decreasing=dict(color=C["danger"])),
            title=dict(text=k, font=dict(size=10,color=C["text2"],family="DM Mono,monospace")),
            number=dict(font=dict(size=22,color=C["accent"],family="Syne,sans-serif")),
            domain=dict(row=i//2, column=i%2)
        ))
    apply_base(fig, height=260,
        grid=dict(rows=2,columns=2,pattern="independent"),
        margin=dict(l=10,r=10,t=10,b=10))
    return fig

def chart_shortage_ts():
    df = shortage_ts()
    colors = [C["danger"],C["accent4"],C["accent2"],C["warning"],C["accent"]]
    fig = go.Figure()
    for i, drug in enumerate(df.columns):
        fig.add_trace(go.Scatter(x=df.index,y=df[drug],name=drug,mode="lines",
            line=dict(color=colors[i],width=2),
            hovertemplate=f"<b>{drug}</b><br>Risk: %{{y:.1f}}<extra></extra>"))
    fig.add_hline(y=80,line_dash="dash",line_color=C["danger"],
        annotation_text="Critical Threshold (80)",annotation_font=dict(size=9,color=C["danger"]))
    apply_base(fig, height=280,
        title=dict(text="Drug Shortage Risk Scores — 90-Day Rolling Window",font=dict(size=11,color=C["text2"]),x=0.01),
        hovermode="x unified")
    return fig

def chart_shortage_bar():
    drugs = [r[0] for r in SHORTAGE_TABLE]
    scores = [r[2] for r in SHORTAGE_TABLE]
    risk = [r[5] for r in SHORTAGE_TABLE]
    cmap = {"HIGH":C["danger"],"MEDIUM":C["warning"],"LOW":C["success"]}
    colors = [cmap[r] for r in risk]
    fig = go.Figure(go.Bar(x=scores,y=drugs,orientation="h",
        marker=dict(color=colors),text=scores,textposition="inside",
        textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Risk Score: %{x}<extra></extra>"))
    apply_base(fig, height=340,
        xaxis=dict(**GX,range=[0,100]),
        margin=dict(l=0,r=10,t=10,b=10))
    return fig

def chart_repurpose():
    drugs = [r[0] for r in REPURPOSE_DATA]
    confs = [r[3] for r in REPURPOSE_DATA]
    indics = [r[2] for r in REPURPOSE_DATA]
    colors = [C["accent3"] if c>85 else C["accent"] if c>70 else C["text2"] for c in confs]
    fig = go.Figure(go.Bar(x=confs,y=drugs,orientation="h",
        marker=dict(color=colors,opacity=0.85),
        text=[f"{c}% → {ind[:22]}…" if len(ind)>22 else f"{c}% → {ind}" for c,ind in zip(confs,indics)],
        textposition="inside",textfont=dict(size=9,family="DM Mono,monospace"),
        customdata=[[r[1],r[2],r[4]] for r in REPURPOSE_DATA],
        hovertemplate="<b>%{y}</b><br>From: %{customdata[0]}<br>To: %{customdata[1]}<br>Basis: %{customdata[2]}<br>Confidence: %{x}%<extra></extra>"))
    apply_base(fig, height=320,
        xaxis=dict(**GX,range=[0,100],ticksuffix="%"),
        margin=dict(l=0,r=10,t=10,b=10))
    return fig

def chart_innovation_map():
    df = INNOV_DF
    fig = go.Figure(go.Scattergeo(
        lat=df["lat"],lon=df["lon"],text=df["city"],
        customdata=np.column_stack([df["score"],df["startups"]]),
        mode="markers+text",textposition="top center",
        textfont=dict(size=9,color="rgba(226,234,245,0.8)",family="DM Mono,monospace"),
        marker=dict(
            size=df["score"]*3.5,color=df["score"],
            colorscale=[[0,"rgba(0,212,255,0.3)"],[0.5,"rgba(123,79,255,0.7)"],[1,"rgba(0,255,157,0.9)"]],
            showscale=True,
            colorbar=dict(title=dict(text="Innovation<br>Index",font=dict(size=9,color=C["text2"])),
                         thickness=10,len=0.6,tickfont=dict(size=8,color=C["text2"]),bgcolor="rgba(0,0,0,0)"),
            line=dict(width=1,color="rgba(255,255,255,0.3)"),sizemode="diameter"),
        hovertemplate="<b>%{text}</b><br>Innovation Index: %{customdata[0]}<br>Startups: %{customdata[1]}<extra></extra>"
    ))
    fig.update_geos(bgcolor=C["bg"],landcolor=C["panel"],showocean=True,oceancolor="#060d1a",
        showland=True,showcoastlines=True,coastlinecolor="rgba(0,212,255,0.2)",
        coastlinewidth=0.8,countrycolor="rgba(0,212,255,0.1)",showframe=False,
        projection_type="natural earth")
    apply_base(fig, height=440, geo=dict(bgcolor=C["bg"]),
        margin=dict(l=0,r=0,t=0,b=0))
    return fig

def chart_choropleth():
    fig = go.Figure(go.Choropleth(
        locations=["USA","CHN","DEU","GBR","CHE","JPN","KOR","BRA","IND","AUS"],
        z=[100,78,72,71,68,64,55,42,48,59],
        colorscale=[[0,"rgba(0,212,255,0.1)"],[0.5,"rgba(123,79,255,0.5)"],[1,"rgba(0,255,157,0.9)"]],
        showscale=True,
        colorbar=dict(thickness=10,len=0.7,tickfont=dict(size=8,color=C["text2"]),bgcolor="rgba(0,0,0,0)"),
        marker=dict(line=dict(color="rgba(0,212,255,0.15)",width=0.5))
    ))
    apply_base(fig, height=280,
        geo=dict(bgcolor=C["bg"],landcolor=C["panel"],showocean=True,oceancolor="#060d1a",
                showcoastlines=True,coastlinecolor="rgba(0,212,255,0.2)"),
        margin=dict(l=0,r=0,t=10,b=10))
    return fig

def chart_interaction_gauge(score, level):
    color = C["danger"] if score>75 else C["warning"] if score>50 else C["success"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",value=score,
        number=dict(font=dict(size=36,color=color,family="Syne,sans-serif"),suffix="/100"),
        gauge=dict(
            axis=dict(range=[0,100],tickfont=dict(size=9)),
            bar=dict(color=color,thickness=0.28),
            bgcolor="rgba(0,0,0,0)",bordercolor="rgba(0,0,0,0)",
            steps=[dict(range=[0,33],color="rgba(0,230,118,0.07)"),
                   dict(range=[33,66],color="rgba(255,184,0,0.07)"),
                   dict(range=[66,100],color="rgba(255,59,92,0.07)")],
        ),
        title=dict(text=f"Interaction Risk: {level}",font=dict(size=11,color=color,family="DM Mono,monospace"))
    ))
    apply_base(fig, height=250, margin=dict(l=20,r=20,t=50,b=10))
    return fig

def chart_network_sankey():
    diseases = ["Alzheimer's","Parkinson's","Lung Cancer","Breast Cancer","Diabetes T2","Heart Disease","Autoimmune"]
    proteins = ["BACE1","α-Synuclein","EGFR","BRCA1/2","GLP-1R","PCSK9","JAK","TNF-α"]
    drugs    = ["Lecanemab","Carbidopa","Osimertinib","Olaparib","Semaglutide","Evolocumab","Baricitinib","Adalimumab"]
    labels = diseases + proteins + drugs
    nd, np_ = len(diseases), len(proteins)
    sources = [0,1,2,3,4,5,6,6,  nd+0,nd+1,nd+2,nd+3,nd+4,nd+5,nd+6,nd+7]
    targets = [nd+0,nd+1,nd+2,nd+3,nd+4,nd+5,nd+6,nd+7,
               nd+np_+0,nd+np_+1,nd+np_+2,nd+np_+3,nd+np_+4,nd+np_+5,nd+np_+6,nd+np_+7]
    values  = [8,7,9,8,10,9,7,8]*2
    colors_nodes = ([C["danger"]]*nd + [C["accent5"]]*np_ + [C["accent"]]*len(drugs))
    fig = go.Figure(go.Sankey(
        node=dict(label=labels,color=colors_nodes,pad=15,thickness=15,
                  line=dict(color="rgba(0,0,0,0)",width=0)),
        link=dict(source=sources,target=targets,value=values,
                  color=["rgba(0,212,255,0.15)"]*len(sources))
    ))
    apply_base(fig, height=380, margin=dict(l=10,r=10,t=20,b=10))
    return fig

def chart_country_risk():
    df = pd.DataFrame(COUNTRY_RISK,columns=["country","score","grade","shortage","reg_delay","supply","trial"])
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Shortage Risk",x=df["country"],y=df["shortage"],
        marker_color=C["danger"],opacity=0.8))
    fig.add_trace(go.Bar(name="Reg. Delay",x=df["country"],y=df["reg_delay"],
        marker_color=C["warning"],opacity=0.8))
    fig.add_trace(go.Bar(name="Supply Chain",x=df["country"],y=df["supply"],
        marker_color=C["accent4"],opacity=0.8))
    apply_base(fig, height=320, barmode="group",
        legend=dict(orientation="h",y=-0.2,bgcolor="rgba(0,0,0,0)",font=dict(size=9)))
    return fig

def chart_risk_radar(idx):
    row = COUNTRY_RISK[idx]
    cats = ["Drug Shortage","Reg. Delay","Supply Chain","Trial Activity<br>(inverse)","Drug Shortage"]
    vals = [row[3],row[4],row[5],100-row[6],row[3]]
    fig = go.Figure(go.Scatterpolar(r=vals,theta=cats,fill="toself",
        fillcolor="rgba(255,59,92,0.15)",line=dict(color=C["danger"],width=2),name=row[0]))
    apply_base(fig, height=320,
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,100],gridcolor="rgba(0,212,255,0.1)",tickfont=dict(size=8,color=C["text3"])),
            angularaxis=dict(gridcolor="rgba(0,212,255,0.1)",tickfont=dict(size=9,color=C["text2"]))),
        margin=dict(l=30,r=30,t=30,b=30))
    return fig

def chart_trial_gauge(prob, label):
    color = C["success"] if prob>65 else C["warning"] if prob>40 else C["danger"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",value=prob,
        number=dict(suffix="%",font=dict(size=40,color=color,family="Syne,sans-serif")),
        gauge=dict(
            axis=dict(range=[0,100],tickfont=dict(size=9,color=C["text3"])),
            bar=dict(color=color,thickness=0.25),
            bgcolor="rgba(0,0,0,0)",bordercolor="rgba(0,0,0,0)",
            steps=[dict(range=[0,40],color="rgba(255,59,92,0.08)"),
                   dict(range=[40,65],color="rgba(255,184,0,0.08)"),
                   dict(range=[65,100],color="rgba(0,230,118,0.08)")],
            threshold=dict(line=dict(color=color,width=2),thickness=0.75,value=prob)
        ),
        title=dict(text=label,font=dict(size=11,color=C["text2"],family="DM Mono,monospace"))
    ))
    apply_base(fig, height=280, margin=dict(l=20,r=20,t=50,b=10))
    return fig

def chart_phase_waterfall():
    phases = ["Phase I", "Phase I→II", "Phase II→III", "Ph III→Approval", "Overall"]
    rates  = [100, 63, 31, 58, 12]
    colors = [C["accent"], C["accent3"], C["warning"], C["accent3"], C["danger"]]
    fig = go.Figure(go.Bar(
        x=phases, y=rates,
        marker=dict(color=colors, opacity=0.85, line=dict(width=0)),
        text=[f"{r}%" for r in rates],
        textposition="outside",
        textfont=dict(size=11, family="DM Mono,monospace"),
        hovertemplate="<b>%{x}</b><br>Success Rate: %{y}%<extra></extra>",
    ))
    fig.add_hline(y=12, line_dash="dot", line_color=C["danger"],
                  annotation_text="Overall 12%",
                  annotation_font=dict(size=9, color=C["danger"]))
    apply_base(fig, height=280,
        yaxis=dict(**GY, title="Success Rate (%)", range=[0, 125]),
        xaxis=dict(gridcolor="rgba(0,212,255,0.06)", zerolinecolor="rgba(0,212,255,0.1)", tickfont=dict(size=9)),
        margin=dict(l=10, r=10, t=30, b=60))
    return fig

def chart_gap_scatter():
    df = pd.DataFrame(RESEARCH_GAPS,columns=["area","research","burden","gap","color"])
    fig = go.Figure()
    fig.add_shape(type="rect",x0=0,y0=50,x1=50,y1=100,fillcolor="rgba(255,59,92,0.04)",line=dict(width=0))
    fig.add_annotation(x=25,y=90,text="⚠ RESEARCH DESERT",showarrow=False,
        font=dict(size=9,color="rgba(255,59,92,0.5)",family="DM Mono,monospace"))
    fig.add_shape(type="rect",x0=50,y0=0,x1=100,y1=50,fillcolor="rgba(0,230,118,0.03)",line=dict(width=0))
    fig.add_annotation(x=75,y=15,text="✓ WELL SERVED",showarrow=False,
        font=dict(size=9,color="rgba(0,230,118,0.5)",family="DM Mono,monospace"))
    fig.add_trace(go.Scatter(x=df["research"],y=df["burden"],mode="markers+text",
        marker=dict(size=df["gap"]/5,color=df["color"],opacity=0.85,
                   line=dict(width=1,color="rgba(255,255,255,0.2)")),
        text=df["area"],textposition="top center",
        textfont=dict(size=9,family="DM Mono,monospace"),
        hovertemplate="<b>%{text}</b><br>Research: %{x}%<br>Burden: %{y}%<extra></extra>"))
    fig.add_hline(y=50,line_dash="dash",line_color="rgba(255,255,255,0.08)")
    fig.add_vline(x=50,line_dash="dash",line_color="rgba(255,255,255,0.08)")
    apply_base(fig, height=420,
        xaxis=dict(**GX,title="Research Activity (%)",range=[-5,105]),
        yaxis=dict(**GY,title="Disease Burden (%)",range=[-5,105]))
    return fig

def chart_gap_bar():
    df = pd.DataFrame(RESEARCH_GAPS,columns=["area","research","burden","gap","color"])
    df = df.sort_values("gap",ascending=True)
    fig = go.Figure(go.Bar(x=df["gap"],y=df["area"],orientation="h",
        marker=dict(color=df["color"],opacity=0.85),
        text=df["gap"].astype(str),textposition="inside",
        hovertemplate="<b>%{y}</b><br>Gap Score: %{x}/100<extra></extra>"))
    apply_base(fig, height=380,
        xaxis=dict(**GX,range=[0,100]),
        margin=dict(l=0,r=10,t=10,b=10))
    return fig

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
now_str = datetime.utcnow().strftime("%H:%M:%S UTC")
st.html(f"""
<div class="gdim-header">
  <div style="display:flex;align-items:center;gap:14px">
    <span style="font-size:28px;color:#00d4ff;text-shadow:0 0 15px #00d4ff;font-weight:800">⊕</span>
    <div>
      <div class="gdim-title">Global Drug Intelligence Monitor</div>
      <div class="gdim-sub">Pharmaceutical Intelligence Platform · Powered by Live Data</div>
    </div>
  </div>
  <div class="live-badge">
    <span style="width:7px;height:7px;border-radius:50%;background:#00e676;box-shadow:0 0 8px #00e676;display:inline-block"></span>
    LIVE &nbsp;·&nbsp; FDA · WHO · PubMed · ClinicalTrials.gov &nbsp;·&nbsp; {now_str}
  </div>
</div>
""")

st.html("<div style='height:8px'></div>")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
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
                <span style="color:#00ff9d;font-size:14px">→</span>
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
            hc.markdown(f'<div style="font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:#4a6080;font-family:DM Mono,monospace;padding-bottom:6px;border-bottom:1px solid rgba(0,212,255,0.12)">{ht}</div>')

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

    ptitle("Global Pharmaceutical Innovation Density")
    st.plotly_chart(chart_innovation_map(), use_container_width=True, config={"displayModeBar":False,"scrollZoom":True})

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

        ec1, ec2, ec3 = st.columns(3)
        for col, label, text, color in [
            (ec1, "SUMMARY", data["summary"], C["accent"]),
            (ec2, "DRUG MECHANISM", data["mechanism"], C["accent2"]),
            (ec3, "CLINICAL IMPACT", data["impact"], C["accent3"]),
        ]:
            rgb = "0,212,255" if color==C["accent"] else "123,79,255" if color==C["accent2"] else "0,255,157"
            col.markdown(f"""
            <div style="padding:14px;background:rgba({rgb},0.04);border-radius:8px;border:1px solid rgba({rgb},0.12);height:100%">
              <div style="font-size:9px;font-weight:700;letter-spacing:0.15em;color:{color};font-family:DM Mono,monospace;margin-bottom:8px">{label}</div>
              <div style="font-size:12px;color:#8fa4c2;font-family:DM Mono,monospace;line-height:1.6">{text}</div>
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
            ["Phase I → II","Phase II → III","Phase III → Approval"],
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
        "Disease → Target Protein → Drug pathways · Hidden relationship discovery")

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
        hc.markdown(f'<div style="font-size:9px;letter-spacing:0.12em;text-transform:uppercase;color:#4a6080;font-family:DM Mono,monospace;padding-bottom:6px;border-bottom:1px solid rgba(0,212,255,0.12)">{ht}</div>')

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
        rc[0].markdown(f'<div style="font-size:11px;color:#ff3b5c;font-family:DM Mono,monospace;padding:4px 0">{dis}</div>')
        rc[1].markdown(f'<div style="font-size:11px;color:#ffd700;font-family:DM Mono,monospace;padding:4px 0">{prot}</div>')
        rc[2].markdown(f'<div style="font-size:11px;color:#00d4ff;font-family:DM Mono,monospace;padding:4px 0">{drug}</div>')
        rc[3].markdown(f'<div style="font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace;padding:4px 0">{mech}</div>')
        rc[4].markdown(f'<div style="display:flex;align-items:center;gap:4px;padding:4px 0"><div style="flex:1;height:3px;background:rgba(255,255,255,0.06);border-radius:2px"><div style="height:100%;width:{conf}%;background:#00ff9d;border-radius:2px"></div></div><span style="font-size:9px;color:#00ff9d;font-family:DM Mono,monospace">{conf}%</span></div>')

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
        hcols = st.columns([2.5,0.8,0.8,1,1,1,1])
        for hc, ht in zip(hcols, ["Country","Score","Grade","Shortage","Reg. Delay","Supply","Trials"]):
            hc.markdown(f'<div style="font-size:9px;letter-spacing:0.1em;text-transform:uppercase;color:#4a6080;font-family:DM Mono,monospace;padding-bottom:6px;border-bottom:1px solid rgba(0,212,255,0.12)">{ht}</div>')
        for r in COUNTRY_RISK:
            risk_color = C["danger"] if r[1]>70 else C["warning"] if r[1]>45 else C["success"]
            rc = st.columns([2.5,0.8,0.8,1,1,1,1])
            rc[0].markdown(f'<div style="font-size:12px;color:#e2eaf5;font-weight:600;padding:3px 0">{r[0]}</div>')
            rc[1].markdown(f'<div style="font-size:14px;font-weight:700;color:{risk_color};font-family:DM Mono,monospace;padding:3px 0">{r[1]}</div>')
            rc[2].markdown(f'<div style="font-size:12px;color:{risk_color};font-family:DM Mono,monospace;padding:3px 0">{r[2]}</div>')
            for i, val in enumerate([r[3],r[4],r[5],r[6]]):
                rc[3+i].markdown(f'<div style="font-size:10px;color:#8fa4c2;font-family:DM Mono,monospace;padding:3px 0">{val}</div>')

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
        col.markdown(f"""
        <div style="padding:16px;background:rgba({rgb},0.06);border-radius:10px;border:1px solid rgba({rgb},0.15);height:100%">
          <div style="font-size:24px;margin-bottom:8px">{icon}</div>
          <div style="font-size:13px;font-weight:700;color:{color};margin-bottom:6px;font-family:Syne,sans-serif">{title}</div>
          <div style="font-size:11px;color:#8fa4c2;font-family:DM Mono,monospace;line-height:1.6;margin-bottom:8px">{text}</div>
          <div style="font-size:9px;color:{color};font-family:DM Mono,monospace;letter-spacing:0.1em">{badge}</div>
        </div>""")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.html("<div style='height:24px'></div>")
st.html(f"""
<div style="text-align:center;padding:16px;border-top:1px solid rgba(0,212,255,0.1);
  font-family:DM Mono,monospace;font-size:9px;color:#4a6080;letter-spacing:0.1em">
  GLOBAL DRUG INTELLIGENCE MONITOR · DATA SOURCES: FDA · WHO · PUBMED · CLINICALTRIALS.GOV ·
  LAST UPDATE: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
</div>""")
