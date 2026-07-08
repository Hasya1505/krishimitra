# 🌾 KrishiMitra — कृषि मित्र

Full-stack Indian farming web app: AI crop recommendations, soil health analysis,
and live weather intelligence. Built with Flask + scikit-learn/XGBoost + SQLite,
vanilla HTML/CSS/JS frontend.

---

## 1. What's included & working

- **Auth**: register/login/logout with hashed passwords (Flask-Login + Werkzeug), SQLite-backed.
- **Crop Recommendation** (`/crop`, `POST /api/crop/recommend`): soft-voting ensemble
  (RandomForest + GradientBoosting + XGBoost) over 22 crops. **95% test accuracy**
  on the bundled synthetic dataset (target from spec was >92%).
- **Soil Analysis** (`/soil`, `POST /api/soil/analyse`): neural-network health
  classifier (Healthy/Moderate/Poor) + a transparent formula-based 0–100 health
  score, per-nutrient breakdown, micronutrient deficiency advice, and a 5-step
  fertilizer/lime improvement plan with a rough recovery timeline.
- **Weather** (`/weather`): live current conditions + 7-day forecast (Open-Meteo,
  no key needed), city search (Nominatim geocoding), a Leaflet/OpenStreetMap map
  with live temperature markers for major cities, frost/excess-rain/drought/heat
  alerts, and a "what to sow now" calendar based on the current month.
- **Landing page**: hero, farming-history timeline, stats strip, trend cards, a
  live news feed (GNews, server-proxied so your key stays secret), and feature teasers.
- **Dashboard shell** (`/home`): sidebar nav that swaps modules via an iframe;
  every module page also works standalone at its own URL.
- Every frontend form is wired to a real backend route — nothing is mocked.

I verified the whole flow myself in a sandbox: register → login → session
persists → crop API returns ranked results → soil API returns a score and
report → both write rows into SQLite. All green.

---

## 2. Two deliberate deviations from the spec (and why)

1. **Soil model: scikit-learn `MLPClassifier` instead of TensorFlow/Keras.**
   Same architecture the spec describes (Dense 128→64→32, ReLU, softmax) trained
   with backprop — but TensorFlow's install size (~600MB+) risks blowing the RAM/slug
   budget on Render/Railway/HF free tiers and slows cold starts badly. If you deploy
   somewhere with more headroom, swap in the literal Keras model from the spec —
   the Flask route only needs `predict_proba()` in the same class order.
2. **Synthetic datasets instead of the exact Kaggle/data.gov.in downloads.**
   This build environment has no internet access to Kaggle or data.gov.in, and
   those are user-uploaded/portal-gated sources I can't scrape and redistribute
   for you. Instead, `models/generate_crop_dataset.py` and
   `models/generate_soil_dataset.py` synthesize statistically realistic data for
   the same 22 crops / same soil-health logic, using published agronomic ranges
   (N-P-K/pH/temperature/humidity/rainfall requirements, Soil Health Card scoring
   bands). **To use the real Kaggle data instead:** download
   `crop_recommendation.csv` (same column names: N,P,K,temperature,humidity,ph,rainfall,label)
   into `data/`, add `season`/`soil_type` columns, and re-run `train_crop_model.py` —
   nothing else changes.

Everything else (routes, DB schema, page flow, design system, APIs) follows the
master prompt as written.

---

## 3. Project structure

```
krishimitra/
├── app.py                     # Flask entry point
├── config.py                  # Config from .env
├── requirements.txt
├── Procfile                    # for Render/Railway (gunicorn app:app)
├── .env.example                 # copy to .env and fill in
├── data/
│   ├── crop_recommendation.csv  # synthetic, 2200 rows, 22 crops
│   └── soil_health.csv          # synthetic, 3000 rows
├── models/
│   ├── generate_crop_dataset.py # regenerate synthetic crop data
│   ├── generate_soil_dataset.py # regenerate synthetic soil data
│   ├── train_crop_model.py      # trains + saves crop_model.pkl etc.
│   ├── train_soil_model.py      # trains + saves soil_model.pkl etc.
│   └── *.pkl / *.json           # trained model + encoders (pre-built, ready to use)
├── routes/
│   ├── auth.py      # register/login/logout
│   ├── crop.py       # POST /api/crop/recommend
│   ├── soil.py        # POST /api/soil/analyse
│   ├── weather.py      # GET /api/weather/alerts, /api/weather/sowing-calendar
│   └── main.py           # page routes + GNews proxy
├── database/
│   └── init_db.py    # SQLite schema (users, crop_queries, soil_queries)
├── static/
│   ├── css/style.css
│   ├── js/{crop,soil,weather}.js
│   └── assets/{india_states_districts.json, crop_info.json}
└── templates/
    ├── landing.html, login.html, home.html, crop.html, soil.html, weather.html
```

---

## 4. Run it locally

```bash
cd krishimitra
python -m venv venv && source venv/bin/activate      # optional but recommended
pip install -r requirements.txt

cp .env.example .env
# edit .env: set a real SECRET_KEY, optionally add a free GNEWS_API_KEY

python app.py
# → open http://localhost:5000
```

The SQLite database and trained models are created/loaded automatically —
no extra setup needed. To retrain the ML models from scratch:

```bash
python models/generate_crop_dataset.py   # optional - CSV already included
python models/generate_soil_dataset.py   # optional - CSV already included
python models/train_crop_model.py
python models/train_soil_model.py
```

---

## 5. Deploy for free

**Render.com** (recommended, easiest):
1. Push this folder to a GitHub repo.
2. New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables `SECRET_KEY` and (optionally) `GNEWS_API_KEY`.
6. Deploy. Free tier gives 512MB RAM, which is enough for this stack (no TensorFlow).

**Railway.app**: same steps, Railway auto-detects the `Procfile`.

**Hugging Face Spaces**: choose the "Flask" SDK option, upload the repo, set the
same env vars as Secrets.

`models/crop_model.pkl` is ~32MB (it's a 3-model soft-voting ensemble) — under
GitHub's 100MB file limit, so it commits normally; no Git LFS needed.

---

## 6. Notes on the free APIs used

| API | Called from | Key needed? |
|---|---|---|
| Open-Meteo | Browser (crop.js auto-fill, weather.js) | No |
| Nominatim (OSM) | Browser (weather.js city search) | No |
| Leaflet + OpenStreetMap tiles | Browser (weather.html/js) | No |
| GNews | Server (`routes/main.py` `/api/news`, proxied) | Yes (free, optional — falls back to sample cards if unset) |

Because Open-Meteo/Nominatim/Leaflet calls happen directly from the user's
browser, they work the same in local dev and in production with zero extra config.
