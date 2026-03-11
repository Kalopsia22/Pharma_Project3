# Global Drug Intelligence Monitor — Plotly Dash App

## Quick Start

### 1. Install dependencies
```bash
pip install dash dash-bootstrap-components plotly pandas numpy
```

### 2. Run the app
```bash
python gdim_app.py
```

### 3. Open in browser
```
http://localhost:8050
```

---

## Features

| Tab | Description |
|-----|-------------|
| 🔬 Drug Discovery | Live publication trend lines, 5–10 year AI forecast bar chart, stacked PubMed area chart, live animated KPI gauges |
| 🔄 Repurposing Engine | Confidence bar chart, interactive candidate table with inline progress bars |
| ⚠️ Shortage Monitor | Live 90-day risk score time series with threshold lines, risk bar chart |
| ⚗️ Interaction AI | Enter any two drugs → instant interaction gauge + mechanism panel |
| 🌍 Innovation Map | Plotly geo scatter with bubble sizing by innovation score |
| 📄 Paper Explainer | Enter any topic → AI-structured Summary / Mechanism / Clinical Impact |
| 🧪 Trial Predictor | Configure 5 parameters → animated gauge + risk factor bars |
| 🕸️ Disease Network | Sankey flow: Disease → Protein → Drug |
| 📊 Risk Index | Grouped bar chart + per-country radar chart |
| 🎯 Research Gaps | Bubble scatter matrix + gap score ranking |

## Live Data Simulation
- **5-second tick** updates publication counts, shortage scores, and KPI gauges
- Shortage time series adds new data points in real time
- Trial predictor gauge animates to the computed probability

## Requirements
- Python 3.9+
- dash >= 2.0
- plotly >= 5.0
- dash-bootstrap-components >= 1.0
- pandas, numpy
