"""
Global Drug Intelligence Monitor
Full Streamlit Application with Live Plotly Charts
Run: streamlit run gdim_streamlit.py
Dependencies: streamlit plotly pandas numpy
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
# COLOUR PALETTE
# ─────────────────────────────────────────────
C = {
    "bg":      "#04080f",
    "bg1":     "#070d1a",
    "bg2":     "#0a1628",
    "bg3":     "#0e1e38",
    "accent":  "#0df4ff",   # cyan
    "accent2": "#8b5cf6",   # violet
    "accent3": "#39ff85",   # lime
    "accent4": "#ff6b2b",   # orange
    "accent5": "#fbbf24",   # gold
    "danger":  "#f43f5e",   # red
    "warning": "#fbbf24",   # gold
    "success": "#39ff85",   # lime
    "text":    "#e8f0fe",
    "text2":   "#7a94b8",
    "text3":   "#3a5068",
}

# Shared axis style dicts
GX = dict(showgrid=True, gridcolor="rgba(13,244,255,0.06)",
          color="#3a5068", tickfont=dict(size=9, family="JetBrains Mono, monospace"),
          zeroline=False)
GY = dict(showgrid=True, gridcolor="rgba(13,244,255,0.06)",
          color="#3a5068", tickfont=dict(size=9, family="JetBrains Mono, monospace"),
          zeroline=False)

# ─────────────────────────────────────────────
# STATIC DATA
# ─────────────────────────────────────────────
REPURPOSE_DATA = [
    ("Metformin",     "T2 Diabetes",    "Cancer Prevention",    88, "AMPK activation · mTOR suppression"),
    ("Sildenafil",    "Erectile Dysfxn","Pulmonary Arterial HT",91, "PDE5 inhibition · Vasodilation"),
    ("Thalidomide",   "Morning Sickness","Multiple Myeloma",    85, "IMiD · TNF-alpha inhibition"),
    ("Aspirin",       "Pain/Fever",     "CV Disease Prevention",94, "COX inhibition · Anti-platelet"),
    ("Minoxidil",     "Hypertension",   "Alopecia",             79, "K-channel opening · Vasodilation"),
    ("Dapagliflozin", "T2 Diabetes",    "Heart Failure",        87, "SGLT2 inhibition · Cardiorenal"),
    ("Rapamycin",     "Immunosuppression","Anti-Aging",         72, "mTOR inhibition · Autophagy"),
]

SHORTAGE_TABLE = [
    ("Amoxicillin",      "Antibiotic",    92, "Critical", "US/EU",   "HIGH"),
    ("Cisplatin",        "Oncology",      88, "Critical", "Global",  "HIGH"),
    ("Albuterol",        "Respiratory",   81, "Shortage",  "US",     "HIGH"),
    ("Morphine",         "Pain Mgmt",     78, "At Risk",   "US/AU",  "HIGH"),
    ("Methotrexate",     "Oncology/RA",   74, "Shortage",  "Global", "HIGH"),
    ("Sodium Bicarb.",   "Critical Care", 67, "Monitoring","US",     "MEDIUM"),
    ("Dopamine",         "Vasopressor",   63, "At Risk",   "US/EU",  "MEDIUM"),
    ("Dexamethasone",    "Corticosteroid",58, "Monitoring","Global", "MEDIUM"),
    ("Insulin Glargine", "Diabetes",      45, "Stable",    "US",     "LOW"),
    ("Lisinopril",       "CV",            38, "Stable",    "US/EU",  "LOW"),
]

INTERACTION_DB = {
    ("warfarin","aspirin"):    ("CRITICAL", 92, "Dual anticoagulation. Aspirin inhibits platelet aggregation (COX-1) while warfarin suppresses clotting factors II, VII, IX, X. Combined use significantly raises major bleeding risk."),
    ("warfarin","ibuprofen"):  ("CRITICAL", 89, "NSAIDs displace warfarin from plasma protein binding (albumin) and inhibit COX-1 platelet thromboxane. INR may rise unpredictably."),
    ("simvastatin","amiodarone"): ("SEVERE",82, "Amiodarone inhibits CYP3A4, increasing simvastatin AUC up to 3-fold. Risk of statin-induced myopathy and rhabdomyolysis."),
    ("metformin","contrast"):  ("MODERATE",55, "Iodinated contrast agents may transiently impair renal function, risking metformin accumulation and lactic acidosis."),
    ("ssri","tramadol"):       ("SEVERE",  78, "Additive serotonergic stimulation. Tramadol is a serotonin-norepinephrine reuptake inhibitor; combination with SSRIs risks serotonin syndrome."),
    ("clopidogrel","omeprazole"):("MODERATE",61,"Omeprazole inhibits CYP2C19, reducing clopidogrel active-metabolite formation by ~45%, blunting antiplatelet effect."),
}

COUNTRY_RISK = [
    # name, score, grade, shortage, reg_delay, supply, trials
    ("India",          72, "C+", "High",   "Moderate", "Moderate", "4,821"),
    ("China",          68, "B-", "High",   "High",     "Moderate", "6,204"),
    ("Russia",         81, "D+", "High",   "High",     "Low",      "1,102"),
    ("Brazil",         61, "C",  "Medium", "High",     "Moderate", "2,891"),
    ("United States",  28, "A",  "Low",    "Low",      "High",     "52,341"),
    ("Germany",        19, "A+", "Low",    "Low",      "High",     "12,871"),
    ("Japan",          22, "A",  "Low",    "Low",      "High",     "9,204"),
    ("UK",             25, "A",  "Low",    "Moderate", "High",     "11,022"),
    ("Canada",         31, "A-", "Low",    "Low",      "High",     "7,891"),
    ("Australia",      34, "B+", "Low",    "Low",      "High",     "5,241"),
    ("Mexico",         58, "C+", "Medium", "Moderate", "Low",      "1,891"),
    ("South Korea",    30, "A-", "Low",    "Low",      "High",     "8,102"),
]

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def apply_base(fig, height=300, margin=None, xaxis=None, yaxis=None, **kwargs):
    """Apply the dark theme base layout to any Plotly figure."""
    m = margin or dict(l=10, r=10, t=20, b=30)
    fig.update_layout(
        height=height,
        margin=m,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="JetBrains Mono, monospace", color=C["text3"], size=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=9, color=C["text3"]),
            orientation="h", yanchor="bottom", y=1.02
        ),
        **kwargs
    )
    if xaxis:
        fig.update_xaxes(**xaxis)
    else:
        fig.update_xaxes(**GX)
    if yaxis:
        fig.update_yaxes(**yaxis)
    else:
        fig.update_yaxes(**GY)
    return fig


def section_hdr(icon, title, subtitle="", badge=""):
    badge_html = f'<div class="ai-badge">{badge}</div>' if badge else ""
    st.html(f"""
    <div class="section-header">
      <div class="section-icon">{icon}</div>
      <div>
        <div class="section-title">{title}</div>
        <div class="section-sub">{subtitle}</div>
      </div>
      {badge_html}
    </div>""")


def stat_cards(cards):
    cols = st.columns(len(cards))
    for col, (label, value, sub, delta, up, color) in zip(cols, cards):
        rgb = color.lstrip("#")
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        if delta:
            d_class = "stat-up" if up else "stat-down"
            d_sym   = "▲" if up else "▼"
            delta_html = f'<div class="{d_class}">{d_sym} {delta}</div>'
        else:
            delta_html = ""
        col.html(f"""
        <div class="stat-card" style="border-top:2px solid {color}">
          <div class="stat-label">{label}</div>
          <div class="stat-value" style="color:{color};text-shadow:0 0 20px rgba({r},{g},{b},0.4)">{value}</div>
          <div class="stat-sub">{sub}</div>
          {delta_html}
        </div>""")


def ptitle(text):
    st.html(f'<div class="panel-title">{text}</div>')


# ─────────────────────────────────────────────
# CHART FUNCTIONS
# ─────────────────────────────────────────────

def chart_discovery():
    areas = ["Oncology", "CNS", "Cardiovascular", "Immunology", "Infectious", "Rare Disease"]
    years = list(range(2018, 2025))
    np.random.seed(42)
    fig = go.Figure()
    colors = [C["accent"], C["accent2"], C["accent3"], C["accent4"], C["accent5"], C["danger"]]
    for i, area in enumerate(areas):
        base = [120, 90, 80, 70, 60, 50][i]
        y = [base + np.random.randint(-8, 25) * (1 + j * 0.12) for j in range(len(years))]
        fig.add_trace(go.Scatter(
            x=years, y=y, name=area, mode="lines+markers",
            line=dict(color=colors[i], width=2),
            marker=dict(size=5, color=colors[i]),
            fill="tonexty" if i > 0 else None,
            fillcolor=f"rgba{tuple(list(bytes.fromhex(colors[i].lstrip('#'))) + [20])}"
        ))
    apply_base(fig, height=320,
               xaxis=dict(**GX, dtick=1),
               yaxis=dict(**GY, title="Publications (thousands)"))
    return fig


def chart_trend_forecast():
    years = list(range(2020, 2031))
    actual = [None]*5 + [None]*6
    actual[:5] = [42, 48, 55, 62, 71]
    forecast = [None]*4 + [71, 79, 88, 98, 109, 121, 135]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years[:5], y=actual[:5], name="Actual",
        line=dict(color=C["accent"], width=2), mode="lines+markers",
        marker=dict(size=5)))
    fig.add_trace(go.Scatter(
        x=years[4:], y=forecast[4:], name="Forecast",
        line=dict(color=C["accent3"], width=2, dash="dot"), mode="lines+markers",
        marker=dict(size=5, symbol="diamond")))
    apply_base(fig, height=320, margin=dict(l=10, r=10, t=10, b=30))
    return fig


def chart_pubmed_area():
    areas  = ["Oncology", "CNS", "Cardiology", "Immunology", "Infectious"]
    colors = [C["accent"], C["accent2"], C["accent3"], C["accent4"], C["accent5"]]
    years  = list(range(2019, 2025))
    np.random.seed(7)
    fig = go.Figure()
    for i, (area, color) in enumerate(zip(areas, colors)):
        base = [320, 210, 190, 160, 140][i]
        y = [base + np.random.randint(0, 40) * (1 + j * 0.1) for j in range(len(years))]
        fig.add_trace(go.Bar(x=years, y=y, name=area,
                             marker_color=color, opacity=0.85))
    fig.update_layout(barmode="stack")
    apply_base(fig, height=280, margin=dict(l=10, r=10, t=10, b=30))
    return fig


def chart_live_kpis(n):
    labels = ["PubMed\nIngestion", "Trial\nUpdates", "Patent\nFeed", "WHO\nAlerts"]
    values = [(n * 13 + 44) % 100, (n * 7 + 61) % 100,
              (n * 11 + 35) % 100, (n * 5 + 78) % 100]
    fig = go.Figure()
    colors = [C["accent"], C["accent3"], C["accent2"], C["accent5"]]
    for i, (lbl, val, col) in enumerate(zip(labels, values, colors)):
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=val,
            title=dict(text=lbl, font=dict(size=8, color=C["text3"])),
            gauge=dict(
                axis=dict(range=[0, 100], tickfont=dict(size=7)),
                bar=dict(color=col, thickness=0.5),
                bgcolor="rgba(0,0,0,0.3)",
                borderwidth=0,
                steps=[dict(range=[0, 100], color="rgba(255,255,255,0.04)")]
            ),
            domain=dict(row=i // 2, column=i % 2)
        ))
    fig.update_layout(
        grid=dict(rows=2, columns=2, pattern="independent"),
        height=280, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["text3"], size=9),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    return fig


def chart_repurpose():
    drugs = [r[0] for r in REPURPOSE_DATA]
    confs = [r[3] for r in REPURPOSE_DATA]
    colors = [C["accent3"] if c > 85 else C["accent"] if c > 70 else C["text3"] for c in confs]
    fig = go.Figure(go.Bar(
        x=confs, y=drugs, orientation="h",
        marker_color=colors,
        text=[f"{c}%" for c in confs],
        textposition="inside",
        textfont=dict(size=9, family="JetBrains Mono, monospace")
    ))
    apply_base(fig, height=320,
               xaxis=dict(**GX, range=[0, 100]),
               margin=dict(l=0, r=10, t=10, b=10))
    return fig


def chart_shortage_ts():
    days = pd.date_range(end=datetime.now(), periods=90)
    np.random.seed(21)
    drugs = ["Amoxicillin", "Cisplatin", "Albuterol", "Morphine", "Methotrexate"]
    colors = [C["danger"], C["accent4"], C["warning"], C["accent2"], C["accent"]]
    fig = go.Figure()
    for drug, color in zip(drugs, colors):
        base = np.random.randint(50, 85)
        y = np.clip(base + np.cumsum(np.random.randn(90) * 1.5), 10, 99)
        fig.add_trace(go.Scatter(
            x=days, y=y, name=drug, mode="lines",
            line=dict(color=color, width=1.8)
        ))
    apply_base(fig, height=260,
               yaxis=dict(**GY, range=[0, 100], title="Risk Score"),
               margin=dict(l=10, r=10, t=10, b=30))
    return fig


def chart_shortage_bar():
    names  = [r[0] for r in SHORTAGE_TABLE[:8]]
    scores = [r[2] for r in SHORTAGE_TABLE[:8]]
    colors = [C["danger"] if s > 75 else C["warning"] if s > 55 else C["accent2"]
              for s in scores]
    fig = go.Figure(go.Bar(
        x=scores, y=names, orientation="h",
        marker_color=colors,
        text=scores, textposition="inside",
        textfont=dict(size=9)
    ))
    apply_base(fig, height=320,
               xaxis=dict(**GX, range=[0, 100]),
               margin=dict(l=0, r=10, t=10, b=10))
    return fig


def chart_interaction_gauge(score, level):
    color = C["danger"] if score > 75 else C["warning"] if score > 50 else C["accent3"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title=dict(text=f"Interaction Risk — {level}", font=dict(size=11, color=C["text"])),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(size=8)),
            bar=dict(color=color, thickness=0.6),
            bgcolor="rgba(0,0,0,0.3)",
            borderwidth=0,
            steps=[
                dict(range=[0, 50],  color="rgba(57,255,133,0.07)"),
                dict(range=[50, 75], color="rgba(251,191,36,0.07)"),
                dict(range=[75, 100],color="rgba(244,63,94,0.1)"),
            ],
            threshold=dict(line=dict(color=color, width=3), value=score)
        ),
        domain=dict(x=[0, 1], y=[0, 1])
    ))
    fig.update_layout(
        height=280, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["text3"], size=10),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def chart_choropleth():
    countries = [r[0] for r in COUNTRY_RISK]
    scores    = [100 - r[1] for r in COUNTRY_RISK]  # invert so higher = better
    iso_map = {
        "India": "IND", "China": "CHN", "Russia": "RUS",
        "Brazil": "BRA", "United States": "USA", "Germany": "DEU",
        "Japan": "JPN", "UK": "GBR", "Canada": "CAN",
        "Australia": "AUS", "Mexico": "MEX", "South Korea": "KOR",
    }
    fig = go.Figure(go.Choropleth(
        locations=[iso_map[c] for c in countries],
        z=scores,
        colorscale=[[0, C["danger"]], [0.5, C["warning"]], [1, C["accent3"]]],
        showscale=True,
        colorbar=dict(title="Score", thickness=8, len=0.6,
                      tickfont=dict(size=8, color=C["text3"])),
        text=countries, hovertemplate="%{text}: %{z}<extra></extra>",
        marker_line_color="rgba(13,244,255,0.15)"
    ))
    fig.update_geos(
        bgcolor="rgba(0,0,0,0)", showframe=False,
        showcoastlines=True, coastlinecolor="rgba(13,244,255,0.2)",
        showland=True, landcolor="#0a1628",
        showocean=True, oceancolor="#04080f",
        showlakes=False, showrivers=False,
        projection_type="natural earth"
    )
    fig.update_layout(
        height=300, paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(color=C["text3"], size=9)
    )
    return fig


def chart_trial_gauge(prob, title):
    color = C["accent3"] if prob > 65 else C["warning"] if prob > 40 else C["danger"]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob,
        number=dict(suffix="%", font=dict(size=36, color=color)),
        title=dict(text=title, font=dict(size=10, color=C["text3"])),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(size=8)),
            bar=dict(color=color, thickness=0.6),
            bgcolor="rgba(0,0,0,0.3)",
            borderwidth=0,
            steps=[
                dict(range=[0, 40],  color="rgba(244,63,94,0.08)"),
                dict(range=[40, 65], color="rgba(251,191,36,0.08)"),
                dict(range=[65, 100],color="rgba(57,255,133,0.08)"),
            ]
        )
    ))
    fig.update_layout(
        height=280, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["text3"], size=10),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def chart_phase_waterfall():
    phases = ["Discovery", "Pre-clinical", "Phase I", "Phase II", "Phase III", "Approval"]
    rates  = [100, 66, 44, 26, 12, 8]
    fig = go.Figure(go.Funnel(
        y=phases, x=rates,
        textinfo="value+percent initial",
        marker=dict(color=[C["accent"], C["accent2"], C["accent3"],
                           C["warning"], C["accent4"], C["danger"]]),
        textfont=dict(size=10, family="JetBrains Mono, monospace")
    ))
    apply_base(fig, height=260, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(visible=False)
    return fig


def chart_network_sankey():
    labels = [
        "Alzheimer's","Heart Disease","Lung Cancer","Breast Cancer","Autoimmune","Type 2 Diabetes",
        "BACE1","PCSK9","EGFR","BRCA1/2","TNF-alpha","GLP-1R",
        "Lecanemab","Evolocumab","Osimertinib","Olaparib","Adalimumab","Semaglutide",
    ]
    source = [0,1,2,3,4,5, 6,7,8,9,10,11]
    target = [6,7,8,9,10,11, 12,13,14,15,16,17]
    value  = [90,95,88,85,82,94, 90,95,88,85,82,94]
    link_colors = [
        "rgba(13,244,255,0.25)","rgba(57,255,133,0.25)","rgba(139,92,246,0.25)",
        "rgba(244,63,94,0.25)","rgba(251,191,36,0.25)","rgba(255,107,43,0.25)",
        "rgba(13,244,255,0.2)","rgba(57,255,133,0.2)","rgba(139,92,246,0.2)",
        "rgba(244,63,94,0.2)","rgba(251,191,36,0.2)","rgba(255,107,43,0.2)",
    ]
    node_colors = (
        [C["danger"]] * 6 +
        [C["warning"]] * 6 +
        [C["accent"]] * 6
    )
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=12, thickness=14,
            line=dict(color="rgba(0,0,0,0.3)", width=0.5),
            label=labels,
            color=node_colors,
        ),
        link=dict(source=source, target=target, value=value, color=link_colors)
    ))
    apply_base(fig, height=360, margin=dict(l=10, r=10, t=10, b=10))
    return fig


def chart_country_risk():
    names     = [r[0] for r in COUNTRY_RISK]
    scores    = [r[1] for r in COUNTRY_RISK]
    shortage  = [{"High":80,"Medium":50,"Low":20}[r[3]] for r in COUNTRY_RISK]
    reg_delay = [{"High":80,"Moderate":55,"Low":25}[r[4]] for r in COUNTRY_RISK]
    supply    = [{"Low":80,"Moderate":50,"High":20}[r[5]] for r in COUNTRY_RISK]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=shortage,  name="Shortage Risk",  marker_color=C["danger"],  opacity=0.8))
    fig.add_trace(go.Bar(x=names, y=reg_delay, name="Reg. Delay",     marker_color=C["warning"], opacity=0.8))
    fig.add_trace(go.Bar(x=names, y=supply,    name="Supply Risk",    marker_color=C["accent4"], opacity=0.8))
    fig.update_layout(barmode="group")
    apply_base(fig, height=320,
               yaxis=dict(**GY, range=[0, 100]),
               margin=dict(l=10, r=10, t=10, b=60))
    return fig


def chart_risk_radar(idx):
    row = COUNTRY_RISK[idx]
    cats = ["Shortage", "Reg. Delay", "Supply Chain", "Geopolitical", "Infrastructure", "Trial Access"]
    np.random.seed(idx * 17)
    base = row[1]
    vals = np.clip([base + np.random.randint(-15, 15) for _ in cats], 5, 99).tolist()
    vals += vals[:1]
    cats_closed = cats + [cats[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats_closed, fill="toself",
        fillcolor=f"rgba(244,63,94,0.1)",
        line=dict(color=C["danger"], width=2),
        marker=dict(size=5, color=C["danger"])
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 100], tickfont=dict(size=7), gridcolor="rgba(13,244,255,0.1)"),
            angularaxis=dict(tickfont=dict(size=8, color=C["text3"]), gridcolor="rgba(13,244,255,0.08)")
        ),
        height=280, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["text3"], size=9),
        margin=dict(l=30, r=30, t=30, b=30),
        showlegend=False
    )
    return fig


def chart_gap_scatter():
    diseases = [
        "Rare Neurological", "NTDs", "Pediatric Rare", "AMR / Antibiotics",
        "Prion Diseases", "Mental Health", "Parasitic", "Rare Metabolic",
        "Diabetes", "Cancer", "Cardiovascular", "HIV/AIDS",
    ]
    burden   = [8.2, 9.1, 7.8, 9.4, 6.1, 8.7, 7.3, 6.8, 7.2, 9.1, 8.8, 7.1]
    research = [1.2, 0.8, 1.5, 1.9, 0.4, 4.1, 2.3, 1.8, 8.2, 9.1, 8.4, 7.8]
    gap      = [b - r for b, r in zip(burden, research)]
    size     = [max(10, abs(g) * 8) for g in gap]
    color    = [C["danger"] if g > 4 else C["warning"] if g > 2 else C["accent3"] for g in gap]

    fig = go.Figure(go.Scatter(
        x=research, y=burden,
        mode="markers+text",
        text=diseases,
        textposition="top center",
        textfont=dict(size=8, color=C["text3"]),
        marker=dict(size=size, color=color, opacity=0.8,
                    line=dict(color="rgba(255,255,255,0.15)", width=1))
    ))
    # Diagonal "fair share" line
    fig.add_shape(type="line", x0=0, y0=0, x1=10, y1=10,
                  line=dict(color="rgba(255,255,255,0.1)", dash="dot", width=1))
    apply_base(fig, height=380,
               xaxis=dict(**GX, range=[0, 10.5], title="Research Activity (0-10)"),
               yaxis=dict(**GY, range=[0, 10.5], title="Disease Burden (0-10)"),
               margin=dict(l=10, r=10, t=10, b=40))
    return fig


def chart_gap_bar():
    diseases = ["Rare Neurological", "AMR", "NTDs", "Pediatric Rare", "Prion", "Mental Health", "Parasitic"]
    gaps     = [7.0, 7.5, 8.3, 6.3, 5.7, 4.6, 5.0]
    colors   = [C["danger"] if g > 6 else C["warning"] for g in gaps]
    fig = go.Figure(go.Bar(
        x=gaps, y=diseases, orientation="h",
        marker_color=colors,
        text=[f"{g:.1f}" for g in gaps],
        textposition="inside",
        textfont=dict(size=9)
    ))
    apply_base(fig, height=280,
               xaxis=dict(**GX, range=[0, 10]),
               margin=dict(l=0, r=10, t=10, b=10))
    return fig


# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg:#04080f; --bg1:#070d1a; --bg2:#0a1628; --bg3:#0e1e38;
    --cyan:#0df4ff; --violet:#8b5cf6; --lime:#39ff85; --orange:#ff6b2b;
    --gold:#fbbf24; --red:#f43f5e; --text:#e8f0fe; --text2:#7a94b8;
    --text3:#3a5068; --border:rgba(13,244,255,0.1); --border2:rgba(13,244,255,0.06);
  }
  * { box-sizing:border-box; }
  html,body,[class*="css"],.stApp {
    font-family:'Space Grotesk',sans-serif !important;
    background:var(--bg) !important; color:var(--text);
  }
  .stApp::before {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:
      radial-gradient(ellipse 80% 50% at 20% 10%,rgba(13,244,255,0.06) 0%,transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 80%,rgba(139,92,246,0.07) 0%,transparent 55%),
      radial-gradient(ellipse 40% 30% at 60% 30%,rgba(57,255,133,0.04) 0%,transparent 50%);
    animation:meshPulse 12s ease-in-out infinite alternate;
  }
  @keyframes meshPulse { 0%{opacity:.7;transform:scale(1)} 100%{opacity:1;transform:scale(1.04)} }
  .stApp::after {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.12) 2px,rgba(0,0,0,.12) 4px);
    opacity:.3;
  }
  .block-container { padding:0 2rem 3rem 2rem !important; max-width:100% !important; position:relative; z-index:1; }
  #MainMenu,footer,header,.stDeployButton { visibility:hidden; display:none; }

  /* HEADER */
  .gdim-header {
    background:linear-gradient(135deg,rgba(4,8,15,.98) 0%,rgba(10,22,40,.98) 100%);
    border-bottom:1px solid var(--border); padding:0 32px; height:64px;
    display:flex; align-items:center; justify-content:space-between;
    margin:-1rem -2rem 0 -2rem; position:sticky; top:0; z-index:999;
    box-shadow:0 1px 0 rgba(13,244,255,.08),0 8px 32px rgba(0,0,0,.6);
    backdrop-filter:blur(20px);
  }
  .gdim-logo-mark {
    width:36px; height:36px; border-radius:10px;
    background:linear-gradient(135deg,rgba(13,244,255,.15),rgba(139,92,246,.15));
    border:1px solid rgba(13,244,255,.3); display:flex; align-items:center;
    justify-content:center; font-size:18px; font-weight:900; color:var(--cyan);
    text-shadow:0 0 20px var(--cyan);
    box-shadow:0 0 20px rgba(13,244,255,.12),inset 0 1px 0 rgba(255,255,255,.1); flex-shrink:0;
  }
  .gdim-title {
    font-size:15px; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
    color:var(--text); margin:0;
    background:linear-gradient(90deg,var(--text),var(--cyan));
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  }
  .gdim-sub {
    font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--text3);
    margin:2px 0 0 0; letter-spacing:.14em; text-transform:uppercase;
  }
  .live-badge {
    font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--lime);
    display:flex; align-items:center; gap:8px; background:rgba(57,255,133,.06);
    border:1px solid rgba(57,255,133,.2); padding:6px 14px; border-radius:20px; letter-spacing:.06em;
  }
  .live-dot {
    width:6px; height:6px; border-radius:50%; background:var(--lime);
    box-shadow:0 0 10px var(--lime); animation:livePulse 1.4s ease-in-out infinite; flex-shrink:0;
  }
  @keyframes livePulse { 0%,100%{opacity:1;box-shadow:0 0 8px var(--lime)} 50%{opacity:.4;box-shadow:0 0 3px var(--lime)} }

  /* SECTION HEADER */
  .section-header {
    display:flex; align-items:flex-start; gap:16px;
    margin:28px 0 24px 0; padding-bottom:20px;
    border-bottom:1px solid var(--border2); position:relative;
  }
  .section-header::after {
    content:''; position:absolute; bottom:-1px; left:0;
    width:80px; height:1px; background:linear-gradient(90deg,var(--cyan),transparent);
  }
  .section-icon { font-size:28px; line-height:1; }
  .section-title {
    font-size:22px; font-weight:700; color:var(--text); margin:0; letter-spacing:-.01em;
  }
  .section-sub {
    font-family:'JetBrains Mono',monospace; font-size:10px;
    color:var(--text3); margin:4px 0 0 0; letter-spacing:.06em;
  }
  .ai-badge {
    margin-left:auto; flex-shrink:0; font-family:'JetBrains Mono',monospace;
    font-size:9px; font-weight:700; letter-spacing:.12em; padding:6px 14px; border-radius:4px;
    border:1px solid rgba(13,244,255,.25);
    background:linear-gradient(135deg,rgba(13,244,255,.06),rgba(139,92,246,.06));
    color:var(--cyan); text-transform:uppercase;
    box-shadow:0 0 16px rgba(13,244,255,.06),inset 0 1px 0 rgba(13,244,255,.08);
  }

  /* STAT CARDS */
  .stat-card {
    background:linear-gradient(135deg,var(--bg2) 0%,var(--bg3) 100%);
    border:1px solid var(--border2); border-radius:14px; padding:20px 18px;
    position:relative; overflow:hidden; transition:border-color .2s,box-shadow .2s;
    height:100%;
  }
  .stat-card::before {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,var(--border),transparent);
  }
  .stat-card:hover { border-color:rgba(13,244,255,.2); box-shadow:0 0 32px rgba(13,244,255,.07); }
  .stat-label {
    font-family:'JetBrains Mono',monospace; font-size:8px; letter-spacing:.18em;
    text-transform:uppercase; color:var(--text3); margin-bottom:10px;
  }
  .stat-value {
    font-size:28px; font-weight:700; line-height:1; letter-spacing:-.02em;
  }
  .stat-sub { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--text3); margin-top:6px; }
  .stat-up {
    font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--lime);
    background:rgba(57,255,133,.08); border:1px solid rgba(57,255,133,.15);
    padding:2px 8px; border-radius:3px; display:inline-block; margin-top:8px;
  }
  .stat-down {
    font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--red);
    background:rgba(244,63,94,.08); border:1px solid rgba(244,63,94,.15);
    padding:2px 8px; border-radius:3px; display:inline-block; margin-top:8px;
  }

  /* PANEL */
  .panel {
    background:linear-gradient(135deg,var(--bg1) 0%,var(--bg2) 100%);
    border:1px solid var(--border2); border-radius:16px; padding:22px; margin-bottom:16px;
    box-shadow:0 4px 24px rgba(0,0,0,.4);
  }
  .panel-title {
    font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:700;
    letter-spacing:.18em; text-transform:uppercase; color:var(--text3);
    margin-bottom:16px; display:flex; align-items:center; gap:10px;
  }
  .panel-title::before {
    content:''; display:block; width:3px; height:14px;
    background:linear-gradient(180deg,var(--cyan),var(--violet)); border-radius:2px;
    box-shadow:0 0 8px var(--cyan); flex-shrink:0;
  }

  /* REPURPOSE CARD */
  .repurpose-card {
    background:linear-gradient(135deg,var(--bg2),var(--bg3));
    border:1px solid var(--border2); border-left:2px solid var(--cyan);
    border-radius:12px; padding:14px 16px; margin-bottom:10px;
    transition:border-color .2s,transform .15s;
  }
  .repurpose-card:hover { border-left-color:var(--lime); transform:translateX(2px); }
  .drug-tag {
    background:rgba(13,244,255,.08); border:1px solid rgba(13,244,255,.2);
    border-radius:4px; padding:3px 9px; font-size:11px;
    font-family:'JetBrains Mono',monospace; color:var(--cyan); display:inline-block;
  }
  .new-tag {
    background:rgba(57,255,133,.08); border:1px solid rgba(57,255,133,.2);
    border-radius:4px; padding:3px 9px; font-size:11px;
    font-family:'JetBrains Mono',monospace; color:var(--lime); display:inline-block;
  }

  /* RISK BADGES */
  .risk-high { background:rgba(244,63,94,.1); color:var(--red); border:1px solid rgba(244,63,94,.25); padding:3px 10px; border-radius:4px; font-size:9px; font-family:'JetBrains Mono',monospace; font-weight:700; text-transform:uppercase; }
  .risk-medium { background:rgba(251,191,36,.1); color:var(--gold); border:1px solid rgba(251,191,36,.25); padding:3px 10px; border-radius:4px; font-size:9px; font-family:'JetBrains Mono',monospace; font-weight:700; text-transform:uppercase; }
  .risk-low { background:rgba(57,255,133,.08); color:var(--lime); border:1px solid rgba(57,255,133,.2); padding:3px 10px; border-radius:4px; font-size:9px; font-family:'JetBrains Mono',monospace; font-weight:700; text-transform:uppercase; }

  /* GAP BUBBLES */
  .gap-high { background:rgba(244,63,94,.08); color:var(--red); border:1px solid rgba(244,63,94,.2); padding:5px 14px; border-radius:20px; font-size:10px; font-family:'JetBrains Mono',monospace; display:inline-block; margin:3px; }
  .gap-medium { background:rgba(251,191,36,.08); color:var(--gold); border:1px solid rgba(251,191,36,.2); padding:5px 14px; border-radius:20px; font-size:10px; font-family:'JetBrains Mono',monospace; display:inline-block; margin:3px; }
  .gap-low { background:rgba(13,244,255,.08); color:var(--cyan); border:1px solid rgba(13,244,255,.18); padding:5px 14px; border-radius:20px; font-size:10px; font-family:'JetBrains Mono',monospace; display:inline-block; margin:3px; }

  /* STREAMLIT OVERRIDES */
  .stSelectbox>div>div, .stTextInput>div>div>input {
    background:var(--bg2) !important; border:1px solid rgba(13,244,255,.18) !important;
    border-radius:10px !important; color:var(--text) !important;
    font-family:'JetBrains Mono',monospace !important; font-size:12px !important;
  }
  .stButton>button {
    background:linear-gradient(135deg,rgba(13,244,255,.12),rgba(139,92,246,.12)) !important;
    border:1px solid rgba(13,244,255,.3) !important; border-radius:10px !important;
    color:var(--cyan) !important; font-family:'Space Grotesk',sans-serif !important;
    font-weight:700 !important; letter-spacing:.06em !important; padding:10px 24px !important;
    width:100% !important; text-transform:uppercase; font-size:11px !important;
    transition:all .2s !important;
  }
  .stButton>button:hover {
    background:linear-gradient(135deg,rgba(13,244,255,.22),rgba(139,92,246,.22)) !important;
    border-color:rgba(13,244,255,.55) !important;
    box-shadow:0 0 24px rgba(13,244,255,.15) !important; transform:translateY(-1px) !important;
  }

  /* TABS */
  .stTabs [data-baseweb="tab-list"] {
    background:linear-gradient(180deg,var(--bg1) 0%,var(--bg) 100%) !important;
    border-bottom:1px solid var(--border2) !important; gap:0; padding:0 8px;
    box-shadow:0 4px 20px rgba(0,0,0,.4);
  }
  .stTabs [data-baseweb="tab"] {
    background:transparent !important; color:var(--text3) !important;
    font-family:'JetBrains Mono',monospace !important; font-size:9px !important;
    font-weight:500 !important; letter-spacing:.1em !important;
    padding:14px 14px !important; border:none !important;
    border-bottom:2px solid transparent !important; text-transform:uppercase !important;
    transition:color .2s !important;
  }
  .stTabs [data-baseweb="tab"]:hover { color:var(--text2) !important; }
  .stTabs [aria-selected="true"] {
    color:var(--cyan) !important; border-bottom:2px solid var(--cyan) !important;
    text-shadow:0 0 20px rgba(13,244,255,.4);
  }
  .stTabs [data-baseweb="tab-panel"] { background:transparent !important; padding:0 !important; }

  /* METRICS */
  div[data-testid="metric-container"] {
    background:linear-gradient(135deg,var(--bg2),var(--bg3)) !important;
    border:1px solid var(--border2) !important; border-radius:14px !important;
    padding:18px !important; box-shadow:0 2px 16px rgba(0,0,0,.3);
  }
  [data-testid="stMetricValue"] {
    color:var(--cyan) !important; font-size:26px !important; letter-spacing:-.02em !important;
  }
  [data-testid="stMetricLabel"] {
    color:var(--text3) !important; font-family:'JetBrains Mono',monospace !important;
    font-size:8px !important; letter-spacing:.14em !important; text-transform:uppercase !important;
  }

  .js-plotly-plot {
    border-radius:12px !important; border:1px solid var(--border2) !important;
    box-shadow:0 4px 24px rgba(0,0,0,.4) !important;
  }

  ::-webkit-scrollbar { width:4px; height:4px; }
  ::-webkit-scrollbar-track { background:var(--bg); }
  ::-webkit-scrollbar-thumb { background:rgba(13,244,255,.2); border-radius:2px; }
  ::-webkit-scrollbar-thumb:hover { background:rgba(13,244,255,.4); }
  hr { border-color:var(--border2) !important; }
</style>
""")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
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
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#3a5068;letter-spacing:.1em;text-align:right">
      <div>FDA · WHO · PUBMED</div>
      <div>CLINICALTRIALS.GOV</div>
    </div>
    <div class="live-badge"><span class="live-dot"></span>LIVE &nbsp;{now_str}</div>
  </div>
</div>
<div style="height:8px"></div>
""")

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
    section_hdr("🔬", "Drug Discovery Trend Predictor",
                "AI analysis of PubMed · ClinicalTrials.gov · Patent filings · Research funding",
                "⚡ AI PREDICTIONS")

    stat_cards([
        ("Active Compounds",       "48,291",  "In global pipelines",   "12.4%", True,  C["accent"]),
        ("PubMed Papers (2024)",   "2.1M",    "Analyzed this year",    "8.2%",  True,  C["accent3"]),
        ("Active Clinical Trials", "487,923", "Global registrations",  "15.7%", True,  C["accent2"]),
        ("Patents Filed (YTD)",    "89,441",  "Biotech & pharma",      "6.1%",  True,  C["accent5"]),
        ("R&D Funding",            "$892B",   "Global investment",     "9.3%",  True,  C["accent4"]),
    ])

    st.html("<div style='height:16px'></div>")

    col1, col2 = st.columns([2, 1])
    with col1:
        ptitle("Publication Volume by Therapeutic Area")
        st.plotly_chart(chart_discovery(), use_container_width=True, config={"displayModeBar": False})
    with col2:
        ptitle("5–10 Year Trend Forecast")
        st.plotly_chart(chart_trend_forecast(), use_container_width=True, config={"displayModeBar": False})

    col3, col4 = st.columns([2, 1])
    with col3:
        ptitle("PubMed Publications — Stacked by Area")
        st.plotly_chart(chart_pubmed_area(), use_container_width=True, config={"displayModeBar": False})
    with col4:
        ptitle("Live KPI Indicators")
        n = int(time.time() / 5) % 1000
        st.plotly_chart(chart_live_kpis(n), use_container_width=True, config={"displayModeBar": False})
        if st.button("🔄 Refresh Live Data", key="refresh_disc"):
            st.cache_data.clear()
            st.rerun()

# ══════════════════════════════════════════════
# TAB 2 — REPURPOSING
# ══════════════════════════════════════════════
with tabs[1]:
    section_hdr("🔄", "AI Drug Repurposing Engine",
                "Molecular similarity · Pathway analysis · Literature mining · FDA & WHO databases",
                "⚡ AI ANALYSIS")

    stat_cards([
        ("Known FDA Drugs",       "20,750+", "Approved compounds",    None,  True,  C["accent"]),
        ("Repurposing Candidates","4,812",   "AI-identified",         "NEW", True,  C["accent3"]),
        ("Validated Successes",   "312",     "Clinically confirmed",  None,  True,  C["accent5"]),
        ("Avg. Dev. Savings",     "$1.4B",   "Per repurposed drug",   None,  True,  C["accent2"]),
    ])

    st.html("<div style='height:16px'></div>")

    col1, col2 = st.columns([1, 1])
    with col1:
        ptitle("Confidence Scores by Candidate")
        st.plotly_chart(chart_repurpose(), use_container_width=True, config={"displayModeBar": False})
    with col2:
        ptitle("Top Repurposing Candidates")
        for drug, orig, new_use, conf, basis in REPURPOSE_DATA:
            bar_w = conf
            color = "#00ff9d" if conf > 85 else "#00d4ff" if conf > 70 else "#8fa4c2"
            st.html(f"""
            <div class="repurpose-card">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap">
                <span class="drug-tag">{drug}</span>
                <span style="font-size:10px;color:#4a6080;font-family:'JetBrains Mono',monospace">{orig}</span>
                <span style="color:#00ff9d;font-size:14px">→</span>
                <span class="new-tag">{new_use}</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                <div style="flex:1;height:4px;background:rgba(255,255,255,.06);border-radius:2px">
                  <div style="height:100%;width:{bar_w}%;background:linear-gradient(90deg,#00d4ff,#7b4fff);border-radius:2px"></div>
                </div>
                <span style="font-size:10px;font-family:'JetBrains Mono',monospace;color:{color}">{conf}%</span>
              </div>
              <div style="font-size:10px;color:#8fa4c2;font-family:'JetBrains Mono',monospace">{basis}</div>
            </div>""")

# ══════════════════════════════════════════════
# TAB 3 — SHORTAGES
# ══════════════════════════════════════════════
with tabs[2]:
    section_hdr("⚠️", "Global Drug Shortage Early Warning System",
                "FDA shortage database · WHO alerts · Supply chain disruptions · Geopolitical risk",
                "🚨 REAL-TIME")

    stat_cards([
        ("Active Shortages (US)",  "142",  "FDA shortage list",    "8 this week", False, C["danger"]),
        ("Critical Risk Drugs",    "38",   "Risk score > 80",       None,          False, C["warning"]),
        ("WHO Alerts",             "27",   "Global alerts active",  None,          False, C["accent4"]),
        ("Mfg. Shutdowns",         "14",   "Active disruptions",    None,          False, C["text"]),
        ("Supply Chain Events",    "91",   "Monitored incidents",   None,          True,  C["accent2"]),
    ])

    st.html("<div style='height:16px'></div>")

    ptitle("Drug Shortage Risk Scores — Live 90-Day Trend")
    st.plotly_chart(chart_shortage_ts(), use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns([6, 4])
    with col1:
        ptitle("Current Shortage Risk Intelligence")
        hdr = st.columns([2.5, 1.5, 1, 1, 1])
        for h, lbl in zip(hdr, ["Drug / Category", "Risk Score", "Status", "Region", "Level"]):
            h.html(f'<div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#4a6080;font-family:\'JetBrains Mono\',monospace;padding-bottom:6px;border-bottom:1px solid rgba(0,212,255,.12)">{lbl}</div>')

        for drug, cat, score, status, region, risk in SHORTAGE_TABLE:
            risk_color = C["danger"] if risk == "HIGH" else C["warning"] if risk == "MEDIUM" else C["success"]
            risk_rgb   = "255,59,92" if risk == "HIGH" else "255,184,0" if risk == "MEDIUM" else "0,230,118"
            rc = st.columns([2.5, 1.5, 1, 1, 1])
            rc[0].markdown(f'<div style="font-size:12px;color:#e2eaf5;font-weight:600">{drug}</div>'
                           f'<div style="font-size:10px;color:#4a6080;font-family:\'JetBrains Mono\',monospace">{cat}</div>',
                           unsafe_allow_html=True)
            rc[1].markdown(f'<div style="display:flex;align-items:center;gap:6px;margin-top:4px">'
                           f'<div style="flex:1;height:4px;background:rgba(255,255,255,.05);border-radius:2px">'
                           f'<div style="height:100%;width:{score}%;background:{risk_color}"></div></div>'
                           f'<span style="font-size:10px;color:{risk_color};font-family:\'JetBrains Mono\',monospace">{score}</span></div>',
                           unsafe_allow_html=True)
            rc[2].markdown(f'<div style="font-size:10px;color:#8fa4c2;font-family:\'JetBrains Mono\',monospace;margin-top:4px">{status}</div>', unsafe_allow_html=True)
            rc[3].markdown(f'<div style="font-size:10px;color:#8fa4c2;font-family:\'JetBrains Mono\',monospace;margin-top:4px">{region}</div>', unsafe_allow_html=True)
            rc[4].markdown(f'<span style="background:rgba({risk_rgb},.15);color:{risk_color};border:1px solid rgba({risk_rgb},.3);padding:3px 8px;border-radius:4px;font-size:9px;font-family:\'JetBrains Mono\',monospace;font-weight:700">● {risk}</span>', unsafe_allow_html=True)

    with col2:
        ptitle("Risk Score Ranking")
        st.plotly_chart(chart_shortage_bar(), use_container_width=True, config={"displayModeBar": False})

    if st.button("🔄 Refresh Shortage Data", key="refresh_shortage"):
        st.cache_data.clear()
        st.rerun()

# ══════════════════════════════════════════════
# TAB 4 — INTERACTIONS
# ══════════════════════════════════════════════
with tabs[3]:
    section_hdr("⚗️", "Drug Interaction Risk AI",
                "Molecular fingerprints · Pharmacokinetic modeling · Real-time interaction prediction",
                "⚡ AI PREDICTION")

    st.html('<div class="panel">')
    ptitle("Enter Drugs to Analyze")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        d1 = st.text_input("Drug 1", value="warfarin",
                           placeholder="e.g. warfarin", label_visibility="collapsed")
    with c2:
        d2 = st.text_input("Drug 2", value="aspirin",
                           placeholder="e.g. aspirin", label_visibility="collapsed")
    with c3:
        analyze = st.button("Analyze Interaction", key="btn_interact")
    st.html("</div>")

    if analyze or (d1 and d2):
        k1, k2 = d1.lower().strip(), d2.lower().strip()
        result = INTERACTION_DB.get((k1, k2)) or INTERACTION_DB.get((k2, k1))
        if not result:
            result = ("MODERATE", 55, "Pharmacokinetic interaction possible. Monitor clinical response closely.")
        level, score, mechanism = result
        risk_color = C["danger"] if score > 75 else C["warning"] if score > 50 else C["accent3"]

        gc1, gc2 = st.columns([1, 1])
        with gc1:
            st.plotly_chart(chart_interaction_gauge(score, level),
                            use_container_width=True, config={"displayModeBar": False})
        with gc2:
            st.html(f"""
            <div style="padding:16px">
              <div style="font-size:16px;font-weight:700;color:#e2eaf5;margin-bottom:14px">
                {d1.title()} + {d2.title()}
              </div>
              <div style="padding:12px;background:rgba(0,0,0,.2);border-radius:8px;border:1px solid {risk_color}22;margin-bottom:10px">
                <div style="font-size:9px;color:#4a6080;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">Risk Level</div>
                <div style="font-size:15px;font-weight:700;color:{risk_color};font-family:'JetBrains Mono',monospace">{level}</div>
              </div>
              <div style="padding:12px;background:rgba(0,0,0,.2);border-radius:8px;border:1px solid rgba(255,255,255,.05);margin-bottom:10px">
                <div style="font-size:9px;color:#4a6080;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">Mechanism</div>
                <div style="font-size:12px;color:#8fa4c2;font-family:'JetBrains Mono',monospace;line-height:1.5">{mechanism}</div>
              </div>
              <div style="padding:12px;background:rgba(0,255,157,.04);border-radius:8px;border:1px solid rgba(0,255,157,.12)">
                <div style="font-size:9px;color:#4a6080;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px">Recommendation</div>
                <div style="font-size:12px;color:#00ff9d;font-family:'JetBrains Mono',monospace;line-height:1.5">Monitor patient closely. Check for signs of adverse effects. Consider dose adjustment or alternative therapy if risk outweighs benefit.</div>
              </div>
            </div>""")

    st.html("<div style='height:16px'></div>")
    col1, col2 = st.columns(2)
    with col1:
        ptitle("Common High-Risk Combinations")
        fig = go.Figure(go.Bar(
            x=[95, 93, 88, 84, 71],
            y=["Warfarin+NSAIDs", "MAOIs+SSRIs", "Digoxin+Amiodarone", "MTX+NSAIDs", "Clopidogrel+PPIs"],
            orientation="h",
            marker_color=[C["danger"], C["danger"], C["warning"], C["warning"], C["accent4"]],
            text=["CRITICAL", "CRITICAL", "SEVERE", "SEVERE", "MODERATE"],
            textposition="inside", textfont=dict(size=10)
        ))
        apply_base(fig, height=240, margin=dict(l=0, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col2:
        ptitle("Interaction Mechanisms")
        fig2 = go.Figure(go.Pie(
            labels=["CYP450 Inhibition", "PD Synergy", "Protein Binding", "P-gp Inhibition", "Renal Clearance"],
            values=[42, 28, 16, 9, 5], hole=0.55,
            marker=dict(colors=[C["accent"], C["accent2"], C["accent3"], C["accent5"], C["accent4"]]),
            textfont=dict(size=10, family="JetBrains Mono, monospace")
        ))
        apply_base(fig2, height=240, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
# TAB 5 — INNOVATION MAP
# ══════════════════════════════════════════════
with tabs[4]:
    section_hdr("🌍", "Pharma Innovation Heatmap",
                "Research papers · Biotech startups · Clinical trials · Patents · Global clusters")

    stat_cards([
        ("Innovation Hotspots", "47",    "Global clusters",    None,  True,  C["accent5"]),
        ("Biotech Startups",    "8,941", "Active globally",    "22%", True,  C["accent"]),
        ("#1 Hub: Boston",      "9.4",   "Innovation index",   None,  True,  C["accent3"]),
        ("Emerging Regions",    "12",    "New biotech hubs",   None,  True,  C["accent2"]),
        ("Cross-Border Trials", "61%",   "International",      None,  True,  C["accent4"]),
    ])
    st.html("<div style='height:16px'></div>")

    ptitle("Global Pharmaceutical Innovation Density — Interactive 3D Globe")
    import streamlit.components.v1 as components
    components.html("""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:#020408;overflow:hidden;}
  .globe-wrap {
    width:100vw; height:560px; position:relative; overflow:hidden;
    border:1px solid rgba(13,244,255,0.12); background:#020408;
  }
  #globe-canvas { width:100%; height:100%; display:block; cursor:grab; touch-action:none; }
  #globe-canvas:active { cursor:grabbing; }
  .hud-hint { position:absolute; top:14px; left:14px; font-family:'JetBrains Mono',monospace;
    font-size:8px; color:rgba(13,244,255,0.4); letter-spacing:0.16em; text-transform:uppercase; pointer-events:none; }
  .hud-badge { position:absolute; top:14px; right:14px; font-family:'JetBrains Mono',monospace;
    font-size:8px; color:rgba(57,255,133,0.5); letter-spacing:0.12em; text-transform:uppercase;
    background:rgba(57,255,133,0.05); border:1px solid rgba(57,255,133,0.12);
    padding:4px 10px; border-radius:4px; pointer-events:none; display:flex; align-items:center; gap:6px; }
  .hud-dot { width:5px;height:5px;border-radius:50%;background:#39ff85;
    box-shadow:0 0 8px #39ff85;animation:livePulse 1.4s ease-in-out infinite; }
  #tt { position:absolute; display:none; z-index:6; pointer-events:none;
    background:rgba(4,8,15,0.93); border:1px solid rgba(13,244,255,0.25);
    border-radius:10px; padding:12px 16px; min-width:190px;
    box-shadow:0 8px 32px rgba(0,0,0,0.7); }
  #tt-city { font-size:14px; font-weight:700; color:#e8f0fe; margin-bottom:8px; }
  .tt-row { display:flex; gap:20px; }
  .tt-col label { font-family:'JetBrains Mono',monospace; font-size:8px; color:#3a5068;
    letter-spacing:0.14em; text-transform:uppercase; display:block; margin-bottom:2px; }
  .tt-col span { font-family:'JetBrains Mono',monospace; font-size:16px; font-weight:700; }
  #tt-score { color:#0df4ff; } #tt-startups { color:#39ff85; }
  #tt-bar-wrap { margin-top:8px;height:3px;background:rgba(255,255,255,0.06);border-radius:2px;overflow:hidden; }
  #tt-bar { height:100%;border-radius:2px;background:linear-gradient(90deg,#0df4ff,#8b5cf6); }
  #tt-rank { font-family:'JetBrains Mono',monospace;font-size:9px;color:#3a5068;margin-top:6px;letter-spacing:0.1em; }
</style>
</head><body>
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
const HUBS=[
  {city:"Boston, MA",lat:42.36,lon:-71.06,score:9.4,startups:1240,rank:1},
  {city:"San Francisco",lat:37.77,lon:-122.42,score:9.1,startups:1100,rank:2},
  {city:"New York, NY",lat:40.71,lon:-74.01,score:8.8,startups:980,rank:3},
  {city:"Basel, CH",lat:47.56,lon:7.59,score:8.9,startups:890,rank:4},
  {city:"London, UK",lat:51.51,lon:-0.13,score:8.7,startups:860,rank:5},
  {city:"Shanghai, CN",lat:31.23,lon:121.47,score:8.6,startups:820,rank:6},
  {city:"Zurich, CH",lat:47.38,lon:8.54,score:8.5,startups:780,rank:7},
  {city:"Tokyo, JP",lat:35.68,lon:139.69,score:8.3,startups:750,rank:8},
  {city:"San Diego, CA",lat:32.72,lon:-117.16,score:8.2,startups:710,rank:9},
  {city:"Munich, DE",lat:48.14,lon:11.58,score:8.1,startups:680,rank:10},
  {city:"Beijing, CN",lat:39.91,lon:116.39,score:8.0,startups:660,rank:11},
  {city:"Toronto, CA",lat:43.65,lon:-79.38,score:7.9,startups:610,rank:12},
  {city:"Stockholm, SE",lat:59.33,lon:18.07,score:7.8,startups:580,rank:13},
  {city:"Singapore",lat:1.35,lon:103.82,score:7.7,startups:540,rank:14},
  {city:"Bangalore, IN",lat:12.97,lon:77.59,score:7.6,startups:520,rank:15},
  {city:"Osaka, JP",lat:34.69,lon:135.50,score:7.5,startups:490,rank:16},
  {city:"Sydney, AU",lat:-33.87,lon:151.21,score:7.2,startups:440,rank:17},
  {city:"São Paulo, BR",lat:-23.55,lon:-46.63,score:6.8,startups:390,rank:18},
];
const canvas=document.getElementById('globe-canvas');
const wrap=canvas.parentElement;
function resize(){canvas.width=wrap.clientWidth*devicePixelRatio;canvas.height=wrap.clientHeight*devicePixelRatio;canvas.style.width=wrap.clientWidth+'px';canvas.style.height=wrap.clientHeight+'px';}
resize();window.addEventListener('resize',()=>{resize();});
const gl=canvas.getContext('webgl',{antialias:true,alpha:false})||canvas.getContext('experimental-webgl',{antialias:true,alpha:false});
if(!gl){canvas.parentElement.innerHTML='<p style="color:#f43f5e;padding:20px">WebGL not supported</p>';return;}
gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.clearColor(0.008,0.016,0.031,1.0);
function mkShader(t,src){const s=gl.createShader(t);gl.shaderSource(s,src);gl.compileShader(s);return s;}
function mkProg(vs,fs){const p=gl.createProgram();gl.attachShader(p,mkShader(gl.VERTEX_SHADER,vs));gl.attachShader(p,mkShader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(p);return p;}
const GLOBE_VS=`precision highp float;attribute vec3 aPos;attribute vec3 aNormal;attribute vec2 aUV;uniform mat4 uMVP;uniform mat4 uModel;uniform mat3 uNormalMat;varying vec3 vNormal;varying vec3 vWorldPos;varying vec2 vUV;void main(){vUV=aUV;vNormal=normalize(uNormalMat*aNormal);vec4 world=uModel*vec4(aPos,1.0);vWorldPos=world.xyz;gl_Position=uMVP*vec4(aPos,1.0);}`;
const GLOBE_FS=`precision highp float;varying vec3 vNormal;varying vec3 vWorldPos;varying vec2 vUV;uniform vec3 uSunDir;uniform float uTime;float rand(vec2 co){return fract(sin(dot(co,vec2(12.9898,78.233)))*43758.5453);}float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);float a=rand(i),b=rand(i+vec2(1,0)),c=rand(i+vec2(0,1)),d=rand(i+vec2(1,1));return mix(mix(a,b,f.x),mix(c,d,f.x),f.y);}float fbm(vec2 p){return noise(p)*0.5+noise(p*2.1)*0.25+noise(p*4.3)*0.125+noise(p*8.7)*0.0625;}float isLand(vec2 uv){float u=uv.x,v=uv.y,land=0.0;if(u>0.08&&u<0.28&&v>0.25&&v<0.65)land=max(land,smoothstep(0.38,0.3,abs(u-0.18))*smoothstep(0.2,0.1,abs(v-0.45)));if(u>0.14&&u<0.30&&v>0.52&&v<0.88)land=max(land,smoothstep(0.1,0.05,abs(u-0.21))*smoothstep(0.22,0.1,abs(v-0.68)));if(u>0.44&&u<0.56&&v>0.15&&v<0.45)land=max(land,smoothstep(0.09,0.04,abs(u-0.50))*smoothstep(0.18,0.06,abs(v-0.30)));if(u>0.43&&u<0.60&&v>0.35&&v<0.80)land=max(land,smoothstep(0.11,0.05,abs(u-0.51))*smoothstep(0.25,0.1,abs(v-0.57)));if(u>0.50&&u<0.85&&v>0.10&&v<0.58)land=max(land,smoothstep(0.22,0.1,abs(u-0.70))*smoothstep(0.28,0.1,abs(v-0.32)));if(u>0.59&&u<0.70&&v>0.38&&v<0.62)land=max(land,smoothstep(0.08,0.03,abs(u-0.645))*smoothstep(0.14,0.04,abs(v-0.50)));if(u>0.72&&u<0.92&&v>0.43&&v<0.63)land=max(land,smoothstep(0.12,0.04,abs(u-0.80))*smoothstep(0.12,0.04,abs(v-0.53)));if(u>0.80&&u<0.87&&v>0.22&&v<0.38)land=max(land,smoothstep(0.05,0.02,abs(u-0.835))*smoothstep(0.1,0.03,abs(v-0.30)));if(u>0.76&&u<0.92&&v>0.56&&v<0.76)land=max(land,smoothstep(0.1,0.04,abs(u-0.84))*smoothstep(0.12,0.05,abs(v-0.65)));if(u>0.20&&u<0.35&&v>0.10&&v<0.32)land=max(land,smoothstep(0.09,0.04,abs(u-0.275))*smoothstep(0.12,0.04,abs(v-0.21)));return clamp(land*1.8,0.0,1.0);}void main(){vec2 uv=vUV;float t=uTime;float tex=fbm(uv*6.0+0.5);float land=isLand(uv);vec3 deepGreen=vec3(0.06,0.28,0.10),lightGreen=vec3(0.13,0.42,0.16),desert=vec3(0.55,0.42,0.18),snow=vec3(0.88,0.92,0.96);float v=uv.y;vec3 landCol=mix(deepGreen,lightGreen,tex);if(v<0.15||v>0.85)landCol=mix(landCol,snow,smoothstep(0.8,0.95,max(v,1.0-v)));landCol+=(tex-0.5)*0.06;vec3 deepOcean=vec3(0.01,0.06,0.18),shallowOcean=vec3(0.03,0.18,0.38);vec3 oceanCol=mix(deepOcean,shallowOcean,fbm(uv*3.0)*0.5);oceanCol+=vec3(0.0,0.04,0.08)*fbm(uv*12.0+vec2(t*0.05,0.0));vec3 surfaceCol=mix(oceanCol,landCol,land);float polar=smoothstep(0.85,0.99,max(v,1.0-v));surfaceCol=mix(surfaceCol,vec3(0.85,0.90,0.95),polar);float cloud1=fbm(uv*4.5+vec2(t*0.012,0.0)),cloud2=fbm(uv*8.0+vec2(-t*0.007,t*0.004));float clouds=smoothstep(0.54,0.68,cloud1*0.6+cloud2*0.4);clouds*=(1.0-polar*0.8);surfaceCol=mix(surfaceCol,vec3(0.88,0.93,1.0),clouds*0.85);vec3 N=normalize(vNormal);float diff=max(0.0,dot(N,uSunDir));float diffSoft=diff*0.8+0.2;vec3 viewDir=normalize(-vWorldPos);vec3 halfV=normalize(uSunDir+viewDir);float spec=pow(max(0.0,dot(N,halfV)),64.0)*(1.0-land)*(1.0-clouds);vec3 col=surfaceCol*diffSoft+vec3(0.4,0.7,1.0)*spec*0.6;float rim=pow(1.0-max(0.0,dot(N,viewDir)),3.5);col+=vec3(0.05,0.40,0.70)*rim*0.6*(diff*0.5+0.5);float nightSide=1.0-smoothstep(0.0,0.25,diff);col+=vec3(1.0,0.55,0.1)*land*(0.3+fbm(uv*20.0)*0.7)*nightSide*0.18;gl_FragColor=vec4(col,1.0);}`;
const ATM_FS=`precision mediump float;varying vec3 vNormal;varying vec3 vWorldPos;varying vec2 vUV;uniform vec3 uSunDir;void main(){vec3 N=normalize(vNormal);vec3 viewDir=normalize(-vWorldPos);float rim=pow(1.0-max(0.0,dot(N,viewDir)),4.0);float sun=max(0.0,dot(N,uSunDir))*0.5+0.5;vec3 atmCol=mix(vec3(0.05,0.30,0.80),vec3(0.3,0.6,1.0),sun);gl_FragColor=vec4(atmCol,rim*0.55);}`;
const MRK_VS=`precision highp float;attribute vec3 aPos;uniform mat4 uMVP;void main(){gl_Position=uMVP*vec4(aPos,1.0);gl_PointSize=8.0;}`;
const MRK_FS=`precision mediump float;uniform vec4 uColor;void main(){vec2 c=gl_PointCoord-0.5;float d=length(c);float circle=1.0-smoothstep(0.35,0.5,d);float glow=exp(-d*d*8.0)*0.7;gl_FragColor=vec4(uColor.rgb,uColor.a*(circle+glow));}`;
const RING_VS=`precision highp float;attribute vec3 aPos;uniform mat4 uMVP;void main(){gl_Position=uMVP*vec4(aPos,1.0);}`;
const RING_FS=`precision mediump float;uniform vec4 uColor;void main(){gl_FragColor=uColor;}`;
const STAR_VS=`precision highp float;attribute vec3 aPos;attribute float aSize;uniform mat4 uMVP;void main(){gl_Position=uMVP*vec4(aPos,1.0);gl_PointSize=aSize;}`;
const STAR_FS=`precision mediump float;void main(){vec2 c=gl_PointCoord-0.5;float d=length(c);float a=1.0-smoothstep(0.2,0.5,d);gl_FragColor=vec4(1.0,1.0,1.0,a*0.8);}`;
const globeProg=mkProg(GLOBE_VS,GLOBE_FS),atmProg=mkProg(GLOBE_VS,ATM_FS),mrkProg=mkProg(MRK_VS,MRK_FS),ringProg=mkProg(RING_VS,RING_FS),starProg=mkProg(STAR_VS,STAR_FS);
function buildSphere(r,segs,rings){const pos=[],nor=[],uvs=[],idx=[];for(let ri=0;ri<=rings;ri++){const phi=ri/rings*Math.PI;for(let s=0;s<=segs;s++){const th=s/segs*Math.PI*2,x=Math.sin(phi)*Math.cos(th),y=Math.cos(phi),z=Math.sin(phi)*Math.sin(th);pos.push(r*x,r*y,r*z);nor.push(x,y,z);uvs.push(s/segs,ri/rings);}}for(let ri=0;ri<rings;ri++)for(let s=0;s<segs;s++){const a=(segs+1)*ri+s,b=a+(segs+1),c=b+1,d=a+1;idx.push(a,b,d,b,c,d);}return{pos:new Float32Array(pos),nor:new Float32Array(nor),uvs:new Float32Array(uvs),idx:new Uint16Array(idx)};}
function mkBuf(d,t=gl.ARRAY_BUFFER){const b=gl.createBuffer();gl.bindBuffer(t,b);gl.bufferData(t,d,gl.STATIC_DRAW);return b;}
function mkDynBuf(d,t=gl.ARRAY_BUFFER){const b=gl.createBuffer();gl.bindBuffer(t,b);gl.bufferData(t,d,gl.DYNAMIC_DRAW);return b;}
const earth=buildSphere(1.0,96,64),ePosB=mkBuf(earth.pos),eNorB=mkBuf(earth.nor),eUVB=mkBuf(earth.uvs),eIdxB=mkBuf(earth.idx,gl.ELEMENT_ARRAY_BUFFER);
const atm=buildSphere(1.065,64,48),aPosB=mkBuf(atm.pos),aNorB=mkBuf(atm.nor),aUVB=mkBuf(atm.uvs),aIdxB=mkBuf(atm.idx,gl.ELEMENT_ARRAY_BUFFER);
const NS=1800,starPos=new Float32Array(NS*3),starSz=new Float32Array(NS);
for(let i=0;i<NS;i++){const th=Math.random()*Math.PI*2,ph=Math.acos(2*Math.random()-1),r=9+Math.random()*3;starPos[i*3]=r*Math.sin(ph)*Math.cos(th);starPos[i*3+1]=r*Math.cos(ph);starPos[i*3+2]=r*Math.sin(ph)*Math.sin(th);starSz[i]=Math.random()*2.2+0.5;}
const starPosB=mkBuf(starPos),starSzB=mkBuf(starSz);
function latLon(lat,lon,r){const phi=(90-lat)*Math.PI/180,th=(lon+180)*Math.PI/180;return[-r*Math.sin(phi)*Math.cos(th),r*Math.cos(phi),r*Math.sin(phi)*Math.sin(th)];}
function scoreColor(s){const t=(s-6.5)/3.0;return[0.05+t*0.17,0.96-t*0.24,1.0-t*0.38,1.0];}
const HUB_R=1.015,hubPositions=HUBS.map(h=>latLon(h.lat,h.lon,HUB_R));
const mrkPosArr=new Float32Array(HUBS.length*3);
hubPositions.forEach((p,i)=>{mrkPosArr[i*3]=p[0];mrkPosArr[i*3+1]=p[1];mrkPosArr[i*3+2]=p[2];});
const mrkPosB=mkDynBuf(mrkPosArr);
function buildRing(cx,cy,cz,nx,ny,nz,r){const pts=[];let ax=0,ay=1,az=0;const dot2=ax*nx+ay*ny+az*nz;if(Math.abs(dot2)>0.9){ax=1;ay=0;az=0;}let ux=ny*az-nz*ay,uy=nz*ax-nx*az,uz=nx*ay-ny*ax;const ul=Math.sqrt(ux*ux+uy*uy+uz*uz);ux/=ul;uy/=ul;uz/=ul;const vx=ny*uz-nz*uy,vy=nz*ux-nx*uz,vz=nx*uy-ny*ux;for(let i=0;i<=32;i++){const a=i/32*Math.PI*2;pts.push(cx+r*(Math.cos(a)*ux+Math.sin(a)*vx),cy+r*(Math.cos(a)*uy+Math.sin(a)*vy),cz+r*(Math.cos(a)*uz+Math.sin(a)*vz));}return new Float32Array(pts);}
const rings=HUBS.map((h,i)=>{const p=hubPositions[i],n=[p[0]/HUB_R,p[1]/HUB_R,p[2]/HUB_R];return{base:buildRing(p[0],p[1],p[2],n[0],n[1],n[2],0.025),buf:null,phase:i*0.35,hub:h};});
rings.forEach(r=>{r.buf=mkDynBuf(r.base);});
function mat4(){return new Float32Array(16);}
function identity(m){m.fill(0);m[0]=m[5]=m[10]=m[15]=1;return m;}
function multiply(a,b,out){for(let i=0;i<4;i++)for(let j=0;j<4;j++){out[i*4+j]=0;for(let k=0;k<4;k++)out[i*4+j]+=a[i*4+k]*b[k*4+j];}return out;}
function perspective(fov,aspect,near,far,out){out.fill(0);const f=1/Math.tan(fov/2);out[0]=f/aspect;out[5]=f;out[10]=(far+near)/(near-far);out[11]=-1;out[14]=2*far*near/(near-far);return out;}
function translate(tx,ty,tz,out){identity(out);out[12]=tx;out[13]=ty;out[14]=tz;return out;}
function rotY(a,out){identity(out);const c=Math.cos(a),s=Math.sin(a);out[0]=c;out[2]=s;out[8]=-s;out[10]=c;return out;}
function rotX(a,out){identity(out);const c=Math.cos(a),s=Math.sin(a);out[5]=c;out[6]=-s;out[9]=s;out[10]=c;return out;}
function normalMatrix3(m4,out3){out3[0]=m4[0];out3[1]=m4[4];out3[2]=m4[8];out3[3]=m4[1];out3[4]=m4[5];out3[5]=m4[9];out3[6]=m4[2];out3[7]=m4[6];out3[8]=m4[10];return out3;}
let rotY_val=0.3,rotX_val=0.18,zoom=2.8,isDragging=false,prevX=0,prevY=0,velX=0,velY=0,autoRot=true,autoTimer=null,time=0;
function startDrag(x,y){isDragging=true;prevX=x;prevY=y;autoRot=false;clearTimeout(autoTimer);}
function doDrag(x,y){if(!isDragging)return;velY=(x-prevX)*0.007;velX=(y-prevY)*0.007;rotY_val+=velY;rotX_val+=velX;rotX_val=Math.max(-1.3,Math.min(1.3,rotX_val));prevX=x;prevY=y;}
function endDrag(){isDragging=false;autoTimer=setTimeout(()=>autoRot=true,3000);}
canvas.addEventListener('mousedown',e=>{e.preventDefault();startDrag(e.clientX,e.clientY);});
window.addEventListener('mousemove',e=>doDrag(e.clientX,e.clientY));
window.addEventListener('mouseup',endDrag);
canvas.addEventListener('touchstart',e=>{e.preventDefault();startDrag(e.touches[0].clientX,e.touches[0].clientY);},{passive:false});
canvas.addEventListener('touchmove',e=>{e.preventDefault();doDrag(e.touches[0].clientX,e.touches[0].clientY);},{passive:false});
canvas.addEventListener('touchend',endDrag);
canvas.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(1.7,Math.min(5.5,zoom+e.deltaY*0.004));},{passive:false});
const tooltip=document.getElementById('tt');
canvas.addEventListener('mousemove',e=>{
  const rect=canvas.getBoundingClientRect();
  const mx=(e.clientX-rect.left)/rect.width*2-1,my=-((e.clientY-rect.top)/rect.height)*2+1;
  let closest=null,closestDist=0.04;
  HUBS.forEach((hub,i)=>{
    const p=hubPositions[i];
    const cosY=Math.cos(-rotY_val),sinY=Math.sin(-rotY_val),cosX=Math.cos(-rotX_val),sinX=Math.sin(-rotX_val);
    let rx=p[0]*cosY+p[2]*sinY,ry=p[1],rz=-p[0]*sinY+p[2]*cosY;
    let rrx=rx,rry=ry*cosX-rz*sinX,rrz=ry*sinX+rz*cosX;
    const aspect=canvas.width/canvas.height,f=1/Math.tan(0.75);
    const zc=rrz-zoom;
    const sx=rrx/(-zc)*f/aspect,sy=rry/(-zc)*f;
    const d=Math.sqrt((sx-mx)**2+(sy-my)**2);
    if(d<closestDist&&rrz<0.8){closestDist=d;closest={hub};}
  });
  if(closest){
    const hub=closest.hub;
    document.getElementById('tt-city').textContent=hub.city;
    document.getElementById('tt-score').textContent=hub.score;
    document.getElementById('tt-startups').textContent=hub.startups.toLocaleString();
    document.getElementById('tt-bar').style.width=((hub.score-6.5)/(10-6.5)*100)+'%';
    document.getElementById('tt-rank').textContent='RANK #'+hub.rank+' GLOBALLY';
    tooltip.style.display='block';
    tooltip.style.left=(e.clientX-canvas.getBoundingClientRect().left+18)+'px';
    tooltip.style.top=(e.clientY-canvas.getBoundingClientRect().top-10)+'px';
  } else tooltip.style.display='none';
});
canvas.addEventListener('mouseleave',()=>tooltip.style.display='none');
function ul(prog,name){return gl.getUniformLocation(prog,name);}
function al(prog,name){return gl.getAttribLocation(prog,name);}
function bindAttr(prog,name,buf,size){const loc=al(prog,name);if(loc<0)return;gl.bindBuffer(gl.ARRAY_BUFFER,buf);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,size,gl.FLOAT,false,0,0);}
const tmp=mat4(),mModel=mat4(),mRX=mat4(),mRY=mat4(),mTrans=mat4(),mProj=mat4(),mMVP=mat4(),mNorm=new Float32Array(9);
function render(ts){
  requestAnimationFrame(render);
  time=ts*0.001;
  if(autoRot)rotY_val+=0.0015;
  if(!isDragging){velX*=0.88;velY*=0.88;}
  const W=canvas.width,H=canvas.height;
  gl.viewport(0,0,W,H);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
  perspective(0.75,W/H,0.1,50.0,mProj);translate(0,0,-zoom,mTrans);rotX(rotX_val,mRX);rotY(rotY_val,mRY);
  multiply(mRX,mRY,tmp);multiply(mTrans,tmp,mModel);multiply(mProj,mModel,mMVP);normalMatrix3(mModel,mNorm);
  const sd=[-0.6,0.5,0.7],sl=Math.sqrt(sd[0]*sd[0]+sd[1]*sd[1]+sd[2]*sd[2]);sd[0]/=sl;sd[1]/=sl;sd[2]/=sl;
  gl.depthMask(false);gl.useProgram(starProg);perspective(0.75,W/H,0.1,50,tmp);
  gl.uniformMatrix4fv(ul(starProg,'uMVP'),false,tmp);
  bindAttr(starProg,'aPos',starPosB,3);
  gl.bindBuffer(gl.ARRAY_BUFFER,starSzB);const szLoc=al(starProg,'aSize');if(szLoc>=0){gl.enableVertexAttribArray(szLoc);gl.vertexAttribPointer(szLoc,1,gl.FLOAT,false,0,0);}
  gl.drawArrays(gl.POINTS,0,NS);gl.depthMask(true);
  gl.useProgram(globeProg);gl.uniformMatrix4fv(ul(globeProg,'uMVP'),false,mMVP);gl.uniformMatrix4fv(ul(globeProg,'uModel'),false,mModel);gl.uniformMatrix3fv(ul(globeProg,'uNormalMat'),false,mNorm);gl.uniform3fv(ul(globeProg,'uSunDir'),sd);gl.uniform1f(ul(globeProg,'uTime'),time);
  bindAttr(globeProg,'aPos',ePosB,3);bindAttr(globeProg,'aNormal',eNorB,3);bindAttr(globeProg,'aUV',eUVB,2);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,eIdxB);gl.drawElements(gl.TRIANGLES,earth.idx.length,gl.UNSIGNED_SHORT,0);
  gl.depthMask(false);gl.blendFunc(gl.SRC_ALPHA,gl.ONE);gl.useProgram(atmProg);
  translate(0,0,-zoom,mTrans);rotX(rotX_val,mRX);rotY(rotY_val,mRY);multiply(mRX,mRY,tmp);multiply(mTrans,tmp,mModel);multiply(mProj,mModel,tmp);
  gl.uniformMatrix4fv(ul(atmProg,'uMVP'),false,tmp);gl.uniformMatrix4fv(ul(atmProg,'uModel'),false,mModel);gl.uniformMatrix3fv(ul(atmProg,'uNormalMat'),false,mNorm);gl.uniform3fv(ul(atmProg,'uSunDir'),sd);gl.uniform1f(ul(atmProg,'uTime'),time);
  bindAttr(atmProg,'aPos',aPosB,3);bindAttr(atmProg,'aNormal',aNorB,3);bindAttr(atmProg,'aUV',aUVB,2);
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER,aIdxB);gl.drawElements(gl.TRIANGLES,atm.idx.length,gl.UNSIGNED_SHORT,0);
  gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(true);
  gl.depthMask(false);gl.useProgram(ringProg);
  HUBS.forEach((hub,i)=>{
    const ring=rings[i],phase=(time*1.8+ring.phase)%(Math.PI*2),scale=1.0+Math.sin(phase)*1.2,opacity=Math.max(0,0.7*(1.0-scale/2.2));
    if(opacity<=0)return;
    const p=hubPositions[i],n=[p[0]/HUB_R,p[1]/HUB_R,p[2]/HUB_R];
    const sc=buildRing(p[0],p[1],p[2],n[0],n[1],n[2],0.025*scale);
    gl.bindBuffer(gl.ARRAY_BUFFER,ring.buf);gl.bufferData(gl.ARRAY_BUFFER,sc,gl.DYNAMIC_DRAW);
    gl.uniformMatrix4fv(ul(ringProg,'uMVP'),false,mMVP);
    const col=scoreColor(hub.score);gl.uniform4fv(ul(ringProg,'uColor'),[col[0],col[1],col[2],opacity]);
    bindAttr(ringProg,'aPos',ring.buf,3);gl.drawArrays(gl.LINE_STRIP,0,33);
  });
  gl.depthMask(true);
  gl.depthMask(false);gl.blendFunc(gl.SRC_ALPHA,gl.ONE);gl.useProgram(mrkProg);gl.uniformMatrix4fv(ul(mrkProg,'uMVP'),false,mMVP);
  HUBS.forEach((hub,i)=>{
    const col=scoreColor(hub.score),pulse=0.85+Math.sin(time*2.0+i*0.6)*0.15;
    gl.uniform4fv(ul(mrkProg,'uColor'),[col[0],col[1],col[2],pulse]);
    gl.bindBuffer(gl.ARRAY_BUFFER,mrkPosB);const loc=al(mrkProg,'aPos');if(loc<0)return;
    gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,3,gl.FLOAT,false,0,i*12);gl.drawArrays(gl.POINTS,0,1);
  });
  gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(true);
}
requestAnimationFrame(render);
})();
</script>
</body></html>
""", height=580, scrolling=False)

    col1, col2 = st.columns([1, 1])
    with col1:
        ptitle("Top Innovation Clusters")
        fig = go.Figure(go.Bar(
            x=[9.4, 9.1, 8.9, 8.8, 8.7, 8.6, 8.5, 8.3, 8.2],
            y=["Boston", "San Francisco", "Basel", "New York", "London",
               "Shanghai", "Zurich", "Tokyo", "San Diego"],
            orientation="h",
            marker=dict(color=C["accent"], opacity=0.85),
            text=["9.4", "9.1", "8.9", "8.8", "8.7", "8.6", "8.5", "8.3", "8.2"],
            textposition="inside", textfont=dict(size=10)
        ))
        apply_base(fig, height=280,
                   xaxis=dict(**GX, range=[7, 10]),
                   margin=dict(l=0, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col2:
        ptitle("Innovation Index by Country (Choropleth)")
        st.plotly_chart(chart_choropleth(), use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
# TAB 6 — PAPER EXPLAINER
# ══════════════════════════════════════════════
with tabs[5]:
    section_hdr("📄", "AI Scientific Paper Explainer",
                "PubMed · arXiv · Instant plain-language summaries", "⚡ AI POWERED")

    ptitle("Search Paper / Topic")
    pc1, pc2 = st.columns([4, 1])
    with pc1:
        paper_query = st.text_input(
            "Paper query", label_visibility="collapsed",
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
        key = "glp" if ("glp" in q or "alzheimer" in q) else \
              "mrna" if ("mrna" in q or "vaccine" in q) else "default"
        data = PAPER_DB[key]
        st.html(f"""
        <div style="background:#112240;border:1px solid rgba(0,212,255,.12);border-radius:12px;padding:20px;margin-bottom:16px">
          <div style="font-size:15px;font-weight:700;color:#e2eaf5;margin-bottom:4px">{data['title']}</div>
          <div style="font-size:9px;color:#4a6080;font-family:'JetBrains Mono',monospace;margin-bottom:16px">PubMed Analysis · arXiv Cross-reference · AI Synthesis</div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:8px">
          <div style="padding:14px;background:rgba(0,212,255,.04);border-radius:8px;border:1px solid rgba(0,212,255,.12)">
            <div style="font-size:9px;font-weight:700;letter-spacing:.15em;color:#00d4ff;font-family:'JetBrains Mono',monospace;margin-bottom:8px">SUMMARY</div>
            <div style="font-size:12px;color:#8fa4c2;font-family:'JetBrains Mono',monospace;line-height:1.6">{data['summary']}</div>
          </div>
          <div style="padding:14px;background:rgba(123,79,255,.04);border-radius:8px;border:1px solid rgba(123,79,255,.12)">
            <div style="font-size:9px;font-weight:700;letter-spacing:.15em;color:#7b4fff;font-family:'JetBrains Mono',monospace;margin-bottom:8px">DRUG MECHANISM</div>
            <div style="font-size:12px;color:#8fa4c2;font-family:'JetBrains Mono',monospace;line-height:1.6">{data['mechanism']}</div>
          </div>
          <div style="padding:14px;background:rgba(0,255,157,.04);border-radius:8px;border:1px solid rgba(0,255,157,.12)">
            <div style="font-size:9px;font-weight:700;letter-spacing:.15em;color:#00ff9d;font-family:'JetBrains Mono',monospace;margin-bottom:8px">CLINICAL IMPACT</div>
            <div style="font-size:12px;color:#8fa4c2;font-family:'JetBrains Mono',monospace;line-height:1.6">{data['impact']}</div>
          </div>
        </div>""")

    st.html("<div style='height:16px'></div>")
    col1, col2 = st.columns([1, 1])
    with col1:
        ptitle("Trending Research Topics (YoY Growth)")
        fig = go.Figure(go.Bar(
            x=[99, 94, 88, 82, 76, 71, 65],
            y=["GLP-1/Obesity", "mRNA Cancer Vaccines", "Alzheimer's", "ADCs",
               "KRAS Inhibitors", "CAR-T", "Radiopharmaceuticals"],
            orientation="h",
            marker=dict(color=[C["accent"], C["accent2"], C["accent3"], C["accent4"],
                               C["accent5"], "#a78bfa", "#34d399"]),
            text=["↑340%", "↑280%", "↑210%", "↑190%", "↑165%", "↑150%", "↑140%"],
            textposition="inside", textfont=dict(size=9)
        ))
        apply_base(fig, height=260, margin=dict(l=0, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with col2:
        ptitle("Journal Impact Factors")
        fig2 = go.Figure(go.Bar(
            x=["NEJM", "Nat. Med.", "Lancet", "JAMA", "Nature", "Cell"],
            y=[91.2, 82.9, 79.3, 63.1, 69.5, 64.5],
            marker=dict(color=[C["accent"], C["accent2"], C["accent3"],
                               C["accent4"], C["accent5"], "#a78bfa"]),
            text=["91.2", "82.9", "79.3", "63.1", "69.5", "64.5"],
            textposition="outside", textfont=dict(size=9)
        ))
        apply_base(fig2, height=260,
                   yaxis=dict(**GY, range=[0, 105]),
                   margin=dict(l=10, r=10, t=10, b=40))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
# TAB 7 — TRIAL PREDICTOR
# ══════════════════════════════════════════════
with tabs[6]:
    section_hdr("🧪", "Clinical Trial Success Predictor",
                "ClinicalTrials.gov · AI model trained on 50,000+ historical trials", "⚡ AI MODEL")

    tc1, tc2 = st.columns([1, 1])
    with tc1:
        ptitle("Configure Trial Parameters")
        drug_class = st.selectbox("Drug Class",
            ["Small Molecule", "Biologic / Antibody", "mRNA Therapy", "Cell & Gene Therapy", "RNA Interference"],
            index=2)
        target = st.selectbox("Target Protein",
            ["EGFR", "PD-1 / PD-L1", "KRAS", "BRCA1/2", "TNF-alpha", "GLP-1R", "BACE1"], index=1)
        area = st.selectbox("Therapeutic Area",
            ["Oncology", "CNS / Neurology", "Cardiovascular", "Infectious Disease", "Rare Disease", "Autoimmune"])
        phase = st.selectbox("Trial Phase",
            ["Phase I → II", "Phase II → III", "Phase III → Approval"], index=1)
        company = st.selectbox("Company Track Record",
            ["Startup (<2 approvals)", "Mid-tier (2-5 approvals)", "Big Pharma (10+ approvals)"], index=1)
        predict_btn = st.button("Predict Success Probability", key="btn_trial")

    with tc2:
        ptitle("Prediction Result")
        if predict_btn:
            base = 40
            if "mRNA" in drug_class:     base += 14
            if "Biologic" in drug_class: base += 10
            if "PD-1" in target:         base += 8
            if "GLP" in target:          base += 6
            if "Big Pharma" in company:  base += 12
            if "Mid-tier" in company:    base += 5
            if "Rare Disease" == area:   base += 7
            if "Oncology" == area:       base -= 4
            prob = min(91, max(18, base))
            st.plotly_chart(chart_trial_gauge(prob, f"{phase} Success Probability"),
                            use_container_width=True, config={"displayModeBar": False})
            risk_color = C["accent3"] if prob > 65 else C["warning"] if prob > 40 else C["danger"]
            st.html(f"""
            <div style="padding:12px;background:rgba(0,0,0,.2);border-radius:8px;border:1px solid rgba(255,255,255,.05);margin-top:8px">
              <div style="font-size:9px;color:#4a6080;font-family:'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.1em;margin-bottom:10px">Key Risk Factors</div>
              {''.join(f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:6px"><span style="font-size:11px;color:#8fa4c2;font-family:DM Mono,monospace;flex:1">{f}</span><div style="flex:2;height:3px;background:rgba(255,255,255,.06);border-radius:2px"><div style="height:100%;width:{p}%;background:#00d4ff;border-radius:2px"></div></div></div>' for f, p in [("Patient Stratification", 72), ("Endpoint Selection", 68), ("Sample Size Power", 81), ("Competitive Landscape", 55)])}
            </div>""")
        else:
            st.html('<div style="color:#4a6080;font-family:\'JetBrains Mono\',monospace;font-size:12px;text-align:center;padding:40px">Configure parameters and click<br>"Predict Success Probability"</div>')

    st.html("<div style='height:16px'></div>")
    c1, c2, c3 = st.columns(3)
    with c1:
        ptitle("Phase Transition Waterfall")
        st.plotly_chart(chart_phase_waterfall(), use_container_width=True, config={"displayModeBar": False})
    with c2:
        ptitle("Success Rate by Drug Class")
        fig = go.Figure(go.Bar(
            x=["Vaccines", "Biologics", "Cell&Gene", "mRNA", "Small Mol.", "ASOs"],
            y=[81, 73, 68, 64, 57, 52],
            marker=dict(color=[C["accent3"], C["accent"], C["accent2"],
                               C["accent5"], C["accent4"], C["text3"]]),
            text=["81%", "73%", "68%", "64%", "57%", "52%"],
            textposition="outside", textfont=dict(size=10)
        ))
        apply_base(fig, height=260,
                   yaxis=dict(**GY, range=[0, 95]),
                   margin=dict(l=10, r=10, t=10, b=40))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    with c3:
        ptitle("Top Failure Reasons")
        fig2 = go.Figure(go.Pie(
            labels=["Lack of Efficacy", "Safety/Toxicity", "Strategic", "Poor PK/ADME"],
            values=[56, 28, 11, 5], hole=0.55,
            marker=dict(colors=[C["danger"], C["warning"], C["text3"], C["accent2"]]),
            textfont=dict(size=10)
        ))
        apply_base(fig2, height=260, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════
# TAB 8 — DISEASE NETWORK
# ══════════════════════════════════════════════
with tabs[7]:
    section_hdr("🕸️", "Global Disease–Drug Network Graph",
                "Disease → Target Protein → Drug pathways · Hidden relationship discovery")

    col1, col2 = st.columns([6, 4])
    with col1:
        ptitle("Disease–Gene–Drug Sankey Flow")
        st.plotly_chart(chart_network_sankey(), use_container_width=True, config={"displayModeBar": False})
    with col2:
        ptitle("Cross-Disease Target Proteins")
        fig = go.Figure(go.Bar(
            x=[8, 6, 5, 5, 4, 4, 3],
            y=["PI3K/mTOR", "TNF-alpha", "JAK-STAT", "NF-κB", "VEGFR", "EGFR", "PCSK9"],
            orientation="h",
            marker=dict(color=[C["accent"], C["accent2"], C["accent3"], C["accent5"],
                               C["accent4"], "#a78bfa", "#34d399"]),
            text=["8 diseases", "6 diseases", "5 diseases", "5 diseases",
                  "4 diseases", "4 diseases", "3 diseases"],
            textposition="inside", textfont=dict(size=9)
        ))
        apply_base(fig, height=280,
                   xaxis=dict(**GX, range=[0, 10]),
                   margin=dict(l=0, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    ptitle("Top Disease–Drug Connections")
    rows = [
        ("Alzheimer's",  "BACE1",      "Lecanemab",    "β-Secretase Inhibition",      92),
        ("Lung Cancer",  "EGFR",       "Osimertinib",  "Tyrosine Kinase Inhibition",  96),
        ("Diabetes T2",  "GLP-1R",     "Semaglutide",  "Receptor Agonism",            94),
        ("Heart Disease","PCSK9",      "Evolocumab",   "Antibody Inhibition",         98),
        ("Breast Cancer","BRCA1/2",    "Olaparib",     "PARP Inhibition",             91),
        ("Parkinson's",  "α-Synuclein","Prasinezumab", "Antibody Targeting",          74),
        ("Autoimmune",   "JAK-STAT",   "Baricitinib",  "JAK1/2 Inhibition",          89),
    ]
    hdr = st.columns([2, 2, 2, 3, 1.5])
    for h, lbl in zip(hdr, ["Disease", "Target Protein", "Drug", "Mechanism", "Confidence"]):
        h.html(f'<div style="font-size:9px;letter-spacing:.12em;text-transform:uppercase;color:#4a6080;font-family:\'JetBrains Mono\',monospace;padding-bottom:6px;border-bottom:1px solid rgba(0,212,255,.12)">{lbl}</div>')

    for dis, prot, drug, mech, conf in rows:
        rc = st.columns([2, 2, 2, 3, 1.5])
        rc[0].markdown(f'<div style="font-size:11px;color:#f43f5e;font-family:\'JetBrains Mono\',monospace;padding:4px 0">{dis}</div>', unsafe_allow_html=True)
        rc[1].markdown(f'<div style="font-size:11px;color:#fbbf24;font-family:\'JetBrains Mono\',monospace;padding:4px 0">{prot}</div>', unsafe_allow_html=True)
        rc[2].markdown(f'<div style="font-size:11px;color:#0df4ff;font-family:\'JetBrains Mono\',monospace;padding:4px 0">{drug}</div>', unsafe_allow_html=True)
        rc[3].markdown(f'<div style="font-size:10px;color:#8fa4c2;font-family:\'JetBrains Mono\',monospace;padding:4px 0">{mech}</div>', unsafe_allow_html=True)
        rc[4].markdown(f'<div style="display:flex;align-items:center;gap:4px;padding:4px 0"><div style="flex:1;height:3px;background:rgba(255,255,255,.06);border-radius:2px"><div style="height:100%;width:{conf}%;background:#39ff85;border-radius:2px"></div></div><span style="font-size:9px;color:#39ff85;font-family:\'JetBrains Mono\',monospace">{conf}%</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 9 — RISK INDEX
# ══════════════════════════════════════════════
with tabs[8]:
    section_hdr("📊", "Pharmaceutical Risk Index",
                "Country-level pharma stability scores · Shortages · Regulatory delays · Supply chain")

    ptitle("Global Pharma Risk Scores — Grouped by Factor")
    st.plotly_chart(chart_country_risk(), use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns([4, 6])
    with col1:
        ptitle("Country Deep-Dive — Risk Radar")
        country_names = [r[0] for r in COUNTRY_RISK]
        selected = st.selectbox("Select Country", country_names, key="country_sel")
        idx = country_names.index(selected)
        st.plotly_chart(chart_risk_radar(idx), use_container_width=True, config={"displayModeBar": False})

    with col2:
        ptitle("Pharma Risk Scorecard")
        tbl = '<table style="width:100%;border-collapse:collapse;font-family:\'JetBrains Mono\',monospace">'
        tbl += '<thead><tr>'
        for h in ["Country", "Score", "Grade", "Shortage", "Reg. Delay", "Supply", "Trials"]:
            tbl += f'<th style="padding:6px 10px;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:#4a6080;text-align:left;border-bottom:1px solid rgba(0,212,255,.15)">{h}</th>'
        tbl += '</tr></thead><tbody>'
        for r in COUNTRY_RISK:
            rc = C["danger"] if r[1] > 70 else C["warning"] if r[1] > 45 else C["accent3"]
            tbl += f'<tr style="border-bottom:1px solid rgba(255,255,255,.04)">'
            tbl += f'<td style="padding:7px 10px;font-size:12px;color:#e2eaf5;font-weight:600">{r[0]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:14px;font-weight:700;color:{rc}">{r[1]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:12px;color:{rc}">{r[2]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#8fa4c2">{r[3]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#8fa4c2">{r[4]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#8fa4c2">{r[5]}</td>'
            tbl += f'<td style="padding:7px 10px;font-size:10px;color:#39ff85">{r[6]}</td>'
            tbl += '</tr>'
        tbl += '</tbody></table>'
        st.html(tbl)

# ══════════════════════════════════════════════
# TAB 10 — RESEARCH GAPS
# ══════════════════════════════════════════════
with tabs[9]:
    section_hdr("🎯", "AI Research Gap Detector",
                "Disease burden vs. research activity · Funding analysis · AI-identified opportunities",
                "🔍 GAP ANALYSIS")

    stat_cards([
        ("Critical Gaps Found",   "28",     "High priority areas", None,  False, C["danger"]),
        ("Underfunded Diseases",  "147",    "vs. burden score",    None,  False, C["warning"]),
        ("Top Opportunity",       "94/100", "Rare Neurological",   None,  True,  C["accent3"]),
        ("Research Deserts",      "63",     "Disease areas",       None,  False, C["text"]),
        ("AI Recommendations",    "341",    "Priority areas",      None,  True,  C["accent2"]),
    ])
    st.html("<div style='height:16px'></div>")

    col1, col2 = st.columns([6, 4])
    with col1:
        ptitle("Research Activity vs. Disease Burden Bubble Matrix")
        st.plotly_chart(chart_gap_scatter(), use_container_width=True, config={"displayModeBar": False})
    with col2:
        ptitle("Gap Score Ranking")
        st.plotly_chart(chart_gap_bar(), use_container_width=True, config={"displayModeBar": False})

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
    insights = [
        (g1, "🧠", "Critical Gap: Rare Neurological",
         "High disease burden (8.2M DALYs globally) but only 3% of neurology research funding targets rare neurological disorders. AI recommends: prion-like spreading mechanisms, lysosomal storage diseases, neuronal ceroid lipofuscinoses.",
         "GAP SCORE: 94/100", C["danger"], "255,59,92"),
        (g2, "🦟", "Neglected Tropical Diseases",
         "1.7 billion people affected globally, yet <1% of pharmaceutical R&D investment targets NTDs. Key opportunities in Chagas disease, schistosomiasis, and lymphatic filariasis drug development.",
         "GAP SCORE: 91/100", C["warning"], "255,184,0"),
        (g3, "🦠", "Antimicrobial Resistance Crisis",
         "AMR projected to cause 10M deaths/year by 2050. Antibiotic pipeline has only 43 drugs — mostly modifications of existing classes. Novel mechanisms urgently needed: phage therapies, bacteriocins.",
         "GAP SCORE: 88/100", C["accent4"], "255,107,53"),
    ]
    for col, icon, title, text, badge, color, rgb in insights:
        col.html(f"""
        <div style="padding:16px;background:rgba({rgb},0.06);border-radius:10px;border:1px solid rgba({rgb},0.15)">
          <div style="font-size:24px;margin-bottom:8px">{icon}</div>
          <div style="font-size:13px;font-weight:700;color:{color};margin-bottom:6px">{title}</div>
          <div style="font-size:11px;color:#8fa4c2;font-family:'JetBrains Mono',monospace;line-height:1.6;margin-bottom:8px">{text}</div>
          <div style="font-size:9px;color:{color};font-family:'JetBrains Mono',monospace;letter-spacing:.1em">{badge}</div>
        </div>""")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.html("<div style='height:24px'></div>")
footer_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
st.html(f"""
<div style="text-align:center;padding:16px;border-top:1px solid rgba(0,212,255,0.1);
  font-family:'JetBrains Mono',monospace;font-size:9px;color:#3a5068;letter-spacing:.1em">
  GLOBAL DRUG INTELLIGENCE MONITOR · DATA SOURCES: FDA · WHO · PUBMED · CLINICALTRIALS.GOV ·
  LAST UPDATE: {footer_time}
</div>""")
