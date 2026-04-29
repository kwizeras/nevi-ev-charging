# 🚀 Deployment Guide

This project ships as **two coordinated free deployments**:

| Layer | Hosted on | URL pattern |
|---|---|---|
| 🌐 **Landing page** (`docs/`) | GitHub Pages | `https://<username>.github.io/<repo>/` |
| ⚡ **Live dashboard** (`nevi_dashboard/`) | Streamlit Community Cloud | `https://<app-name>.streamlit.app` |

Together they cost **$0/month** and look fully professional. Follow the steps below in order.

---

## ✅ Pre-flight checklist

- [ ] **Rotate any exposed API keys** before pushing to a public repo
  - Gemini: <https://aistudio.google.com/app/apikey>
  - NREL: <https://developer.nrel.gov/signup/>
- [ ] Confirm `.env` is **not** tracked by git (it's gitignored)
- [ ] Confirm `nevi_dashboard/data/*.csv` is **not** tracked (gitignored)
- [x] Placeholders in `README.md`, `docs/index.html`, and `nevi_dashboard/app.py` have already been filled with your handles
- [ ] After Streamlit Cloud deployment, update the live URL in `README.md` and `docs/index.html` if it differs from `nevi-ev-charging.streamlit.app`

---

## 1️⃣ Push the project to GitHub

```bash
cd "DEVP 226/Final Project"

git init
git add .
git status                  # ← double-check no .env or *.csv is staged
git commit -m "Initial public release: NEVI EV Charging Supply Chain"

# Create the repo on GitHub (public), then:
git branch -M main
git remote add origin https://github.com/kwizeras/nevi-ev-charging.git
git push -u origin main
```

> 💡 Recommended repo name: **`nevi-ev-charging`** or **`ev-charging-supply-chain`**.

---

## 2️⃣ Deploy the dashboard to Streamlit Community Cloud

1. Go to <https://share.streamlit.io/> and sign in with GitHub.
2. Click **New app** → choose your repo and `main` branch.
3. Set **Main file path**: `nevi_dashboard/app.py`
4. Click **Advanced settings** → **Secrets** and paste:

   ```toml
   NREL_API_KEY = "your_real_nrel_key"
   GEMINI_API_KEY = "your_real_gemini_key"
   ```

5. Click **Deploy**. First boot takes ~3–5 min.
6. **Copy the live URL** (e.g. `https://nevi-ev-charging.streamlit.app`).

### ⚠️ Don't forget the data!

The dashboard expects `nevi_dashboard/data/afdc_stations.csv`, but that file is gitignored (it's 80,000+ rows). Three options:

| Option | When to use | How |
|---|---|---|
| **A. Generate at startup** | Recommended for production | Add a tiny snippet in `app.py` that runs `fetch_data.py` if the CSV is missing |
| **B. Commit a sample** | Demo only | Save a 1,000-row sample, commit it, remove it from `.gitignore` |
| **C. Upload via UI** | Interactive | Add an `st.file_uploader` to let users bring their own CSV |

> Below is the snippet for **Option A** (drop into `app.py` near `load_data`):
>
> ```python
> if not Path("data/afdc_stations.csv").exists():
>     with st.spinner("First-time setup: fetching ~80k stations from NREL (≈2 min)…"):
>         from fetch_data import main as fetch_main
>         fetch_main()
> ```

---

## 3️⃣ Enable GitHub Pages for the landing site

1. On GitHub, open your repo → **Settings** → **Pages** (left sidebar).
2. Under **Build and deployment**:
   - **Source**: *Deploy from a branch*
   - **Branch**: `main` → **Folder**: `/docs`
3. Click **Save**. Wait ~1 min.
4. Your landing page will be live at:

   ```
   https://kwizeras.github.io/nevi-ev-charging/
   ```

5. Update `docs/index.html` and `README.md` with the **real** Streamlit URL from step 2.

### 🌍 Custom domain (optional)

If you own `sotairekwizera.com` or similar:

1. In **Settings → Pages → Custom domain**, enter `evcharging.sotairekwizera.com`.
2. Add this DNS CNAME record on your domain registrar:
   ```
   CNAME    evcharging    kwizeras.github.io.
   ```
3. Check **Enforce HTTPS**.

---

## 4️⃣ Final polish (recommended)

### Add screenshots to the README

```bash
# After running the dashboard locally, take 2-3 screenshots
# Save them to: docs/assets/img/
#   - dashboard-map.png
#   - dashboard-charts.png
#   - dashboard-eva.png
```

Then add to the README:

```markdown
## 📸 Screenshots
![Dashboard Map](docs/assets/img/dashboard-map.png)
```

### Add an Open Graph preview image

For nice link previews on LinkedIn / X / Slack:

1. Create a `1200×630` PNG: `docs/assets/img/og-preview.png`
2. Add to `<head>` of `docs/index.html`:
   ```html
   <meta property="og:image" content="https://kwizeras.github.io/nevi-ev-charging/assets/img/og-preview.png">
   ```

### Pin the repo on your GitHub profile

GitHub profile → **Customize your pins** → pin `nevi-ev-charging`. This is the single highest-leverage personal-branding move you can make.

---

## 🔄 Updating after launch

```bash
# Make changes locally, then:
git add .
git commit -m "Update X"
git push

# Streamlit Cloud auto-redeploys on push (~30 seconds)
# GitHub Pages auto-rebuilds on push (~1 min)
```

---

## 🧯 Troubleshooting

| Problem | Fix |
|---|---|
| Streamlit app shows "App is sleeping" | Free tier sleeps after 7 days idle. Click **Wake up**. |
| `ModuleNotFoundError` on Streamlit Cloud | Add the missing package to `nevi_dashboard/requirements.txt` and push |
| Gemini returns 429 | Free tier = 15 req/min. Wait or add a paid tier |
| GitHub Pages 404 | Wait ~5 min after first enable. Confirm `docs/index.html` exists on `main` |
| API key visible in commit history | Rotate the key immediately. Use `git filter-repo` to scrub history |

---

Built by **Sotaire Kwizera** · [GitHub](https://github.com/kwizeras) · [LinkedIn](https://linkedin.com/in/sotairekwizera)
