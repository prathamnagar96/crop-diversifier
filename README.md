# KrishiKavach — crop advice for El Niño-prone Vidarbha

A simple, farmer-friendly app (Marathi / Hindi / English) that recommends
low-risk crops for a likely low-rain El Niño year, explains how to grow them,
collects post-harvest feedback, and has a chat assistant ("Krishi Mitra").

## Run it

```bash
python server.py
```

Then open http://127.0.0.1:8000 — no installs needed (Python 3.9+ standard library only).

## Present it from another device (GitHub Codespaces)

1. Open this repository on GitHub (any laptop/tablet browser, logged in to the repo owner's account).
2. Click **Code → Codespaces → Create codespace on main**.
3. Wait ~1 minute — the app starts automatically and opens in a new tab
   (or open the **Ports** tab and click the globe icon next to port 8000).
4. To show it on a projector or another phone, in **Ports** right-click 8000 → **Port visibility → Public** and share that link.

Optional permanent public link: deploy the repo on [Render](https://render.com) (free) — `render.yaml` is included.

## What's inside

| File | What it does |
|---|---|
| `server.py` | Local web server + JSON API (`/api/meta`, `/api/recommend`, `/api/chat`, `/api/feedback`) |
| `recommender.py` | Explainable crop scoring: soil fit × water balance under the El Niño rain outlook × drought tolerance |
| `chatbot.py` | Krishi Mitra chat — offline answers from the crop knowledge base; optional Claude AI mode |
| `static/` | The app (HTML/CSS/JS, no build step): home, 4-question farm wizard, results, crop guide, harvest feedback, chat |
| `data/feedback.json` | Saved harvest reports (the "what happened after planting" loop) |

## Features

- 4 tap-only questions (district, soil, water source, season) with photo tiles
- Top-3 crops with photo, reasons, water drops, safety dot, earning range; warns if the usual crop (cotton/wheat) is risky
- Crop guide: sowing/harvest calendar, 3 tips, one-tap Kisan helpline (1800-180-1551)
- Read-aloud 🔊 on every screen and voice input in chat (browser speech features)
- Harvest feedback → stored and shown back as "N farmers shared" (the feedback loop for the supervisors' question)

## Turn on AI chat (optional)

By default the chatbot works offline. To use Claude for free-form answers:

```bash
pip install anthropic
```

then set an `ANTHROPIC_API_KEY` environment variable and restart the server. The chat header will
show **AI** instead of **Offline**. It uses `claude-opus-5-5` (change with `KRISHI_MODEL`), low effort,
and server-side refusal fallback; any error falls back to the offline answer.

## Photos

Stock photos are freely licensed (Wikimedia Commons / Flickr via Openverse) and loaded online — see
"Photo credits" in the app. To make them work offline, save each as `static/img/<key>.jpg`
(keys are in `static/images.js`); local files are used automatically.

## Important

All crop numbers, prices and rainfall values are **approximate demo values**. Before real use, replace
them with sourced data (ICRISAT district database, DES, IMD, Agmarknet/MSP) and validate the model with
the El Niño-year backtest described in `presentation-and-defense.md`.
