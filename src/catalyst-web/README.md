# Catalyst — Web Prototype

Clickable hi-fi prototype for the Catalyst product UI.

## Run locally

This is a static site — no build step. From the folder root:

```bash
python -m http.server 8000
# then open http://localhost:8000
```

Or any other static file server (`npx serve`, `http-server`, etc).

> Opening `index.html` directly via `file://` will not work — Babel needs to fetch the JSX files over HTTP.

## Flow

1. **Empty state** — sidebar shows only the Catalyst wordmark and "+ Add catalogue". Centre has a ghosted preview of the populated activation list.
2. **Upload** — click the "+" (or press `N`) to open the dropzone. Drag a `.csv` file or click "Choose file".
3. **Reading** — the catalogue is added to the sidebar with a live progress underline. The centre shows the per-agent trace (`spotify_track`, `instagram_video`, `period_track`, `track_summarizer`, …).
4. **Results** — the activation ranking: hot tracks marked with a cyan dot, per-track LLM reasoning inline on expand, per-platform signal map. Toggle between Seasonal moment and Social trend lenses.

## Stack

- Plain HTML + React 18 (via UMD)
- Babel-standalone for inline JSX (no bundler)
- Tailwind CDN + custom CSS in `styles-prototype.css`
- Fonts: Manrope (sans), JetBrains Mono (mono)

## Structure

```
.
├── index.html
├── styles-prototype.css
└── screens/
    ├── flow/
    │   └── data.js              # Italo Heritage demo data (FLOW_DATA)
    └── prototype/
        ├── icons.jsx             # Wordmark, platform icons, indicators
        ├── sidebar.jsx           # Left navigation (logo, + add, catalogue list)
        ├── empty.jsx             # No-catalogue state with ghosted preview
        ├── upload.jsx            # CSV dropzone
        ├── reading.jsx           # Live agent trace + progress
        ├── results.jsx           # Activation list + per-track expand
        └── app.jsx               # Host + state machine
```

## Wiring to the backend

The prototype currently uses canned demo data from `screens/flow/data.js` regardless of which CSV is uploaded — the filename and estimated track count flow through, but the agent output is fixed. To wire it to the real pipeline:

- Replace the timer-driven progression in `reading.jsx` with a poll against your processing status endpoint
- Replace the `TRACK_DETAILS` map in `results.jsx` with a fetch against `/api/catalogues/{id}/results`
- Surface the real `track_summarizer` / `period_track` outputs into the `reason` and `stats` fields
