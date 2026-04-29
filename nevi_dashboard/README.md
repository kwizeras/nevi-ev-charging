# ⚡ NEVI EV Charging Dashboard

> Interactive Streamlit dashboard exploring 80,000+ U.S. EV charging stations from the Alternative Fuels Data Center, with an embedded AI assistant (EVA) powered by Google Gemini.

This is the **`nevi_dashboard/`** subfolder of the [NEVI EV Charging Supply Chain](../README.md) project. For the full research paper, landing page, and project context, see the [root README](../README.md).

---

## ✨ Features

- 🗺️ **Interactive map** with 4 styles (Dark, Streets, Satellite, Light) and per-station detail
- 📊 **Time-series, network, and state breakdowns** with Plotly
- 🌐 **Choropleth state comparison** with population- and area-normalized metrics
- 🤖 **EVA AI assistant** — ask plain-English questions about the data
- 📥 **CSV export** of any filtered subset
- 🎨 **Custom dark theme** with branded UI

---

## 🚀 Run locally

```bash
# 1. From the repo root
cd nevi_dashboard

# 2. Set up a virtual environment
python -m venv venv
.\venv\Scripts\activate           # Windows
# source venv/bin/activate        # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
#  → edit .env and paste your free NREL + Gemini keys

# 5. Fetch data (~2 min)
python fetch_data.py

# 6. Launch the dashboard
streamlit run app.py
#  → opens http://localhost:8501
```

---

## ☁️ Deploy to Streamlit Community Cloud (free)

1. Push this repo to GitHub (public).
2. Go to <https://share.streamlit.io/> and click **New app**.
3. Point it at `nevi_dashboard/app.py`.
4. In **App settings → Secrets**, paste:

   ```toml
   NREL_API_KEY = "your_real_key"
   GEMINI_API_KEY = "your_real_key"
   ```

5. Click **Deploy**. Done — your app is live at `https://<app-name>.streamlit.app`.

> 📘 Full instructions in [DEPLOYMENT.md](../DEPLOYMENT.md).

---

## 📁 Files

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit dashboard |
| `utils.py` | Data helpers, state metadata, Gemini integration |
| `fetch_data.py` | Pull 80,000+ stations from the NREL API → CSV |
| `analyze_deployment_velocity.py` | Quantitative velocity analysis (paper Section VII) |
| `export_study_data.py` | Generate paper-ready data subsets |
| `collect_nevi_data.py` | Compile NEVI award data |
| `.streamlit/config.toml` | Theme + server settings |
| `.streamlit/secrets.toml.example` | Template for cloud secrets |
| `.env.example` | Template for local environment variables |

---

## 🔐 API keys

You need **two free keys**:

| Service | Free tier | Sign up |
|---|---|---|
| **NREL AFDC** | 1,000 requests/hour | <https://developer.nrel.gov/signup/> |
| **Google Gemini** | 15 requests/min, 1,500/day | <https://aistudio.google.com/app/apikey> |

Both go into `.env` (local) or Streamlit Cloud secrets (production). **Never commit them.**

---

## 🛠️ Tech stack

- **Streamlit 1.31+** for the app framework
- **Pandas / NumPy** for data wrangling
- **Plotly Express** for interactive maps & charts
- **Google Gemini 2.0 Flash** via the `google-genai` SDK
- **python-dotenv** for local secrets

---

Built by **[Sotaire Kwizera](../README.md#-author)** for DEVP 226 at UC Berkeley.
