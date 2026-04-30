# ⚡ NEVI, Utilities, and Installers
### *Bottlenecks in U.S. EV Charging Deployment*

[![Live Dashboard](https://img.shields.io/badge/▶%20Live%20Dashboard-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://nevi-ev-charging.streamlit.app)
[![Project Site](https://img.shields.io/badge/🌐%20Project%20Site-GitHub%20Pages-181717?style=for-the-badge&logo=github&logoColor=white)](https://kwizeras.github.io/nevi-ev-charging/)
[![Read the Paper](https://img.shields.io/badge/📄%20Read%20the%20Paper-PDF-EA4335?style=for-the-badge)](DEVP%20226-Paper%20Final%20Version.pdf)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> An empirical analysis of **9,229 DCFC stations** deployed across all 50 U.S. states (2020–2024), quantifying how federal policy, state institutions, and supply chains shape America's transition to electric mobility.

---

## 🎯 Key Findings

| Finding | Evidence |
|---|---|
| **Federal policy works.** Post-NEVI national deployment accelerated **+153.5%** | 92.1 → 233.4 stations/month |
| **State capacity is the multiplier.** Texas surged +520.8%; California +8.7% (saturated); Mississippi 860% from a near-zero base | Velocity analysis across 9,229 stations |
| **Institutions dominate deployment time.** Permitting + interconnection account for **65–85%** of total lag — not hardware | Bottleneck analysis (Section V of paper) |
| **Network structure matters.** ChargePoint deploys at scale (52/mo, 33.9% share); Tesla deploys for quality (29/mo, >99% uptime) | Network velocity comparison |

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/kwizeras/nevi-ev-charging.git
cd nevi-ev-charging/nevi_dashboard
python -m venv venv
.\venv\Scripts\activate    # Windows
# source venv/bin/activate # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your free API keys:
#   NREL:    https://developer.nrel.gov/signup/
#   Gemini:  https://aistudio.google.com/app/apikey
```

### 3. Fetch data & run

```bash
python fetch_data.py            # ~2 min: pulls 80,000+ stations from NREL
streamlit run app.py            # opens http://localhost:8501
```

---

---

## 🌐 Deployment

This project ships as **two coordinated deployments**:

| Layer | Hosted on | Purpose |
|---|---|---|
| 🌐 **Landing page** (`docs/`) | **GitHub Pages** (free, static) | Showcase findings, link to dashboard & paper |
| ⚡ **Live dashboard** (`nevi_dashboard/`) | **Streamlit Community Cloud** (free) | Interactive Python app with AI assistant |

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions.

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| **Data** | NREL Alternative Fuels Data Center API · pandas · numpy |
| **Visualization** | Plotly Express · Plotly Graph Objects · Folium |
| **App framework** | Streamlit 1.31+ |
| **AI assistant** | Google Gemini 2.0 Flash via `google-genai` |
| **Landing page** | Vanilla HTML/CSS · Inter & Playfair Display fonts |
| **Hosting** | GitHub Pages (static) + Streamlit Community Cloud (Python) |

---

## 📖 The Research Paper

The full empirical paper (Sections I–IX) is available in the repo:

- 📄 [DEVP 226-Paper Final Version.pdf](DEVP%20226-Paper%20Final%20Version.pdf)
- 🌐 [DEVP 226-Paper Final Version.html](DEVP%20226-Paper%20Final%20Version.html)

**Sections include:**
1. Introduction
2. Background & Literature Review
3. Conceptual Framework (supply chain stages A–F)
4. Methodology (velocity analysis, 9,229-station sample)
5. Findings: Bottleneck Analysis (3 dominant bottlenecks)
6. Quantitative Analysis (4 data tables, network breakdown)
7. Policy Implications (4 targeted recommendations)
8. Conclusion

---

## 👤 Author

**Sotaire Kwizera** — Data Analyst · Graduate Student at UC Berkeley

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/sotairekwizera)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?logo=github&logoColor=white)](https://github.com/kwizeras)
[![Email](https://img.shields.io/badge/Email-Contact-EA4335?logo=gmail&logoColor=white)](mailto:kwizeras@berkeley.edu)

---

## 📜 License

MIT © 2026 Sotaire Kwizera — see [LICENSE](LICENSE) for details.

> **Data attribution.** Charging station data is sourced from the U.S. Department of Energy's
> [Alternative Fuels Data Center](https://afdc.energy.gov/), maintained by the National Renewable
> Energy Laboratory (NREL). This project is independent academic work and is not affiliated
> with NREL, DOE, or the Joint Office of Energy and Transportation.

---

<div align="center">
  <sub>Built with ⚡ for DEVP 226: Economics of Innovation and Supply Chains · UC Berkeley · Spring 2026</sub>
</div>
