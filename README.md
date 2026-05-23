# Catalyst

**Music catalogue analysis at scale.**

[Catalyst](https://catalyst-production-6360.up.railway.app) is a multi-agent system that continuously monitors music catalogues across Spotify, Instagram, TikTok, and YouTube, surfaces cultural moments before they pass, and delivers per-track activation intelligence at a scale no human team can match.

Built for the [Featherless Track · AI Agent Olympics · Milan AI Week 2026](https://lablab.ai/ai-hackathons/milan-ai-week-hackathon)


---

## What it does

73% of streams come from catalogue, but catalogue teams are a fraction the size of frontline teams. Catalyst closes that gap by running **14 specialised agents per track**, daily, across four platforms — then synthesising everything into a ranked activation brief.

Each analysis run:
1. Loads a catalogue from CSV
2. Fetches current and historical metrics from Spotify, Instagram, TikTok, and YouTube
3. Runs 14 track-level agents and 9 artist-level agents via [OpenRouter](https://openrouter.ai) (Gemini 3.1 Flash Lite)
4. Produces a per-track summary with seasonal timing, platform signals, and top video context
5. Ranks the catalogue by activation readiness

---

## Architecture

```
CSV upload
    │
    ▼
load_catalogue.py          ← fetches platform metadata, seeds DB
    │
    ▼
14 track agents (parallel-ready, run per track)
    ├── spotify_track / spotify_track_historic
    ├── instagram_track / instagram_track_historic / instagram_video
    ├── tiktok_track / tiktok_track_historic / tiktok_video
    ├── youtube_track / youtube_track_historic / youtube_video / youtube_shorts
    ├── period_track                    ← seasonal/cultural timing
    └── track_summarizer                ← cross-platform synthesis

9 artist agents (run per artist)
    ├── spotify_artist / spotify_artist_historic
    ├── instagram_artist / instagram_artist_historic
    ├── tiktok_artist / tiktok_artist_historic
    ├── youtube_artist / youtube_artist_historic
    └── artist_summarizer

    │
    ▼
FastAPI /api/catalogues/{id}/results   ← ranked activation output
    │
    ▼
React frontend                         ← live trace + results UI
```

### Agent model

Every agent is built on the [Strands](https://github.com/strands-agents/sdk-python) framework. Each one receives a set of `@tool` functions that query the database, calls the LLM (Gemini 3.1 Flash Lite via OpenRouter), and writes its output back to the database. No agent shares state mid-run — they read from DB, reason, write to DB.

The **video pipeline** (`src/agents/video_pipeline.py`) downloads short-form videos via `yt-dlp`, extracts 8 frames with `ffmpeg`, and sends them to a multimodal model (Nemotron 3 Nano Omni via OpenRouter) for a 2–4 sentence description. This feeds the `instagram_video`, `tiktok_video`, `youtube_video`, and `youtube_shorts` agents.

The **period agent** maps each track against 9 cultural anchors (Valentine's Day, Festival Season, Summer, Halloween, Christmas, etc.) and calculates the 90-day pre-peak work window to identify what needs activating now.

---

## Tech stack

| Layer | Technology |
|---|---|
| Inference | [OpenRouter](https://openrouter.ai) — Gemini 3.1 Flash Lite (text), Nemotron 3 Nano Omni (video understanding) |
| Agent framework | [Strands](https://github.com/strands-agents/sdk-python) |
| API | FastAPI + Uvicorn |
| MCP server | FastMCP |
| Database | SQLite via SQLAlchemy 2.0 |
| Data | [Songstats](https://songstats.com) · Spotify API · Last.fm · SoundCloud · MusicBrainz |
| Video | yt-dlp + ffmpeg |
| Frontend | React 18 + Vite · TypeScript · Tailwind CSS v4 |
| Deployment | Railway |
| License | Apache 2.0 |

---

## Setup

### Requirements

- Python 3.11+
- `ffmpeg` installed and on PATH (for video frame extraction)

### Install

```bash
git clone https://github.com/ProjectCatalystAI/catalyst
cd catalyst
pip install -r requirements.txt
```

### Environment variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

| Variable | Source |
|---|---|
| `SPOTIFY_CLIENT_ID` | [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) |
| `SPOTIFY_CLIENT_SECRET` | Same |
| `LASTFM_API_KEY` | [Last.fm API](https://www.last.fm/api/account/create) |
| `LASTFM_API_SECRET` | Same |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) |
| `SONGSTATS_API_KEY` | [Songstats](https://songstats.com/developers) |

---

## Running

### Production (one process)

Build the frontend, then start the API — FastAPI serves both `/api/*` and the built assets from `/`.

```bash
cd frontend && npm install && npm run build
cd ..
uvicorn src.api:app --app-dir backend --reload
```

Open `http://localhost:8000`.

### Development (two terminals, HMR)

```bash
# Terminal 1 — API
uvicorn src.api:app --app-dir backend --reload

# Terminal 2 — Vite dev server with HMR; proxies /api → :8000
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

---

## Project structure

```
backend/
├── requirements.txt
└── src/
    ├── agents/
    │   ├── model.py               # OpenRouter model factory
    │   ├── prompts.py             # System prompts for all 23 agents
    │   ├── video_pipeline.py      # yt-dlp + ffmpeg + vision analysis
    │   ├── tools/
    │   │   ├── db_fetch.py        # @tool functions for DB queries
    │   │   └── period.py          # Cultural calendar tools
    │   ├── spotify_track.py
    │   ├── instagram_track.py
    │   ├── tiktok_track.py
    │   ├── youtube_track.py
    │   ├── period_track.py
    │   ├── track_summarizer.py
    │   └── ...                    # artist-level agents
    ├── api.py                     # FastAPI app + job orchestration
    ├── db.py                      # SQLAlchemy models
    ├── load_catalogue.py          # CSV → DB ingestion pipeline
    ├── streaming_analyst.py       # Platform API integration layer
    ├── import_catalogue.py        # CLI import tool
    ├── server.py                  # FastMCP setup
    └── __main__.py                # MCP entry point

frontend/                      # Vite + React + TypeScript app
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── styles.css
    ├── types.ts
    ├── icons.tsx
    ├── api/catalogues.ts      # typed fetch helpers
    ├── data/flowData.ts       # demo-mode fallback data
    └── components/            # Sidebar / Empty / Upload / Reading / Results
```

---

## License

[Apache 2.0](LICENSE)

---

Built by Kevin, Thomas, and Cele.
