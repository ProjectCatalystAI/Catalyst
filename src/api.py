"""FastAPI surface for the Catalyst analyzer suite.

Run with:
    uvicorn src.api:app --reload
"""

from __future__ import annotations

import logging
import os
import re
import sys
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

# Allow bare imports from src/ (needed by streaming_analyst → server)
_src_dir = str(Path(__file__).parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.agents.runner import (
    ARTIST_AGENT_NAMES,
    TRACK_AGENT_NAMES,
    run_artist_agent,
    run_track_agent,
)
from src.db import (
    Artist,
    Catalog,
    Database,
    InstagramTrack,
    SpotifyTrack,
    TiktokTrack,
    Track,
    YoutubeTrack,
)
from src.load_catalogue import load_catalog_from_csv

logger = logging.getLogger(__name__)

app = FastAPI(title="Catalyst Analyzers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Existing models + endpoints
# ---------------------------------------------------------------------------

class AnalyzeTrackRequest(BaseModel):
    track_id: int = Field(..., description="Primary key of the target track row.")
    agents: list[str] = Field(
        ...,
        description=(
            "Ordered list of analyzer names to invoke. Each name must be one of: "
            + ", ".join(TRACK_AGENT_NAMES)
        ),
    )


class AnalyzeTrackResponse(BaseModel):
    track_id: int
    results: dict[str, str]


class AnalyzeArtistRequest(BaseModel):
    artist_id: int = Field(..., description="Primary key of the target artist row.")
    agents: list[str] = Field(
        ...,
        description=(
            "Ordered list of profile analyzer names to invoke. Each name must "
            "be one of: " + ", ".join(ARTIST_AGENT_NAMES)
        ),
    )


class AnalyzeArtistResponse(BaseModel):
    artist_id: int
    results: dict[str, str]


@app.get("/track-agents")
def list_track_agents() -> dict:
    return {"agents": list(TRACK_AGENT_NAMES)}


@app.get("/artist-agents")
def list_artist_agents() -> dict:
    return {"agents": list(ARTIST_AGENT_NAMES)}


@app.post("/analyze-track", response_model=AnalyzeTrackResponse)
def analyze_track(req: AnalyzeTrackRequest) -> AnalyzeTrackResponse:
    unknown = [a for a in req.agents if a not in TRACK_AGENT_NAMES]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agents: {unknown}. Valid: {list(TRACK_AGENT_NAMES)}",
        )
    results: dict[str, str] = {}
    for name in req.agents:
        results[name] = run_track_agent(name, req.track_id)
    return AnalyzeTrackResponse(track_id=req.track_id, results=results)


@app.post("/analyze-artist", response_model=AnalyzeArtistResponse)
def analyze_artist(req: AnalyzeArtistRequest) -> AnalyzeArtistResponse:
    unknown = [a for a in req.agents if a not in ARTIST_AGENT_NAMES]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agents: {unknown}. Valid: {list(ARTIST_AGENT_NAMES)}",
        )
    results: dict[str, str] = {}
    for name in req.agents:
        results[name] = run_artist_agent(name, req.artist_id)
    return AnalyzeArtistResponse(artist_id=req.artist_id, results=results)


# ---------------------------------------------------------------------------
# Catalogue job tracking (in-memory, reset on restart)
# ---------------------------------------------------------------------------

@dataclass
class _Job:
    job_id: int
    name: str
    track_count: int
    status: str  # pending | loading | analyzing | done | error
    pct: int
    agent: str
    step: str
    catalogue_id: int | None = None
    error: str | None = None


_jobs: dict[int, _Job] = {}
_next_job_id: int = 1
_jobs_lock = threading.Lock()


def _new_job(name: str, track_count: int) -> _Job:
    global _next_job_id
    with _jobs_lock:
        job = _Job(
            job_id=_next_job_id,
            name=name,
            track_count=track_count,
            status="pending",
            pct=0,
            agent="loader",
            step="Queued",
        )
        _jobs[_next_job_id] = job
        _next_job_id += 1
    return job


def _update_job(job_id: int, **kwargs: object) -> None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job:
            for k, v in kwargs.items():
                setattr(job, k, v)


# ---------------------------------------------------------------------------
# Pipeline helpers
# ---------------------------------------------------------------------------

_AGENT_LABEL: dict[str, str] = {
    "spotify_track":           "Pulling Spotify track signals · 90d window",
    "spotify_track_historic":  "Reading Spotify historic curves",
    "instagram_track":         "Pulling Instagram audio reuse",
    "instagram_track_historic":"Reading Instagram historic curves",
    "instagram_video":         "Reading top 5 IG videos per flagged track",
    "tiktok_track":            "Pulling TikTok audio reuse · creator counts",
    "tiktok_track_historic":   "Reading TikTok historic curves",
    "tiktok_video":            "Reading top 5 TikTok videos per flagged track",
    "youtube_track":           "Pulling YouTube long-form views",
    "youtube_track_historic":  "Reading YouTube historic curves",
    "youtube_video":           "Reading top 5 YouTube videos per flagged track",
    "youtube_shorts":          "Reading YouTube Shorts seeding signals",
    "period_track":            "Aligning tracks to calendar windows",
    "track_summarizer":        "Composing per-track reasoning",
    "spotify_artist":          "Reading artist profiles · Spotify",
    "instagram_artist":        "Reading artist profiles · Instagram",
    "tiktok_artist":           "Reading artist profiles · TikTok",
    "youtube_artist":          "Reading artist profiles · YouTube",
    "artist_summarizer":       "Composing per-artist reasoning",
}


def _first_sentence(text: str | None) -> str:
    if not text:
        return ""
    m = re.search(r"(?<=[.!?])\s", text)
    return text[: m.start() + 1].strip() if m else text[:200].strip()


def _signal(views: int | None) -> int:
    if not views:
        return 0
    return 2 if views > 500_000 else 1


def _build_results(catalogue_db_id: int, catalogue_name: str) -> dict:
    db = Database()
    with db.session() as s:
        tracks = s.query(Track).filter_by(catalog_id=catalogue_db_id).all()
        result_tracks = []
        for track in tracks:
            artist = s.get(Artist, track.artist_id)
            sp = s.query(SpotifyTrack).filter_by(track_id=track.id).first()
            ig = s.query(InstagramTrack).filter_by(track_id=track.id).first()
            tt = s.query(TiktokTrack).filter_by(track_id=track.id).first()
            yt = s.query(YoutubeTrack).filter_by(track_id=track.id).first()

            sp_sig = _signal(sp.streams if sp else None)
            ig_sig = _signal(ig.views if ig else None)
            tt_sig = _signal(tt.views if tt else None)
            yt_sig = _signal(yt.video_views if yt else None)
            signals = {
                "spotify": sp_sig,
                "instagram": ig_sig,
                "tiktok": tt_sig,
                "youtube": yt_sig,
            }

            hot_platform = any(v == 2 for v in signals.values())
            seasonal_hot = hot_platform and bool(track.analysis)
            social_hot = hot_platform and bool(track.summary)
            lit = bool(track.summary or track.analysis)
            year = track.release_date.year if track.release_date else None

            seasonal_stats: dict[str, str] = {}
            if sp:
                if sp.streams:
                    seasonal_stats["Streams"] = f"{sp.streams:,}"
                if sp.popularity:
                    seasonal_stats["Popularity"] = str(sp.popularity)
                if sp.playlists_current:
                    seasonal_stats["Playlists"] = f"{sp.playlists_current:,}"

            social_stats: dict[str, str] = {}
            if ig:
                if ig.video_count:
                    social_stats["IG videos"] = str(ig.video_count)
                if ig.views:
                    social_stats["IG views"] = f"{ig.views:,}"
            if tt:
                if tt.creator_reach:
                    social_stats["TT creators"] = f"{tt.creator_reach:,}"
                if tt.views:
                    social_stats["TT views"] = f"{tt.views:,}"
            if yt:
                if yt.video_views:
                    social_stats["YT views"] = f"{yt.video_views:,}"
                if yt.shorts_count:
                    social_stats["YT shorts"] = str(yt.shorts_count)

            result_tracks.append({
                "id": track.id,
                "title": track.title,
                "artist": artist.name if artist else "Unknown",
                "year": year,
                "lit": lit,
                "seasonal": {
                    "synth": _first_sentence(track.analysis),
                    "reason": track.analysis or "",
                    "hot": seasonal_hot,
                    "signals": signals,
                    "stats": seasonal_stats,
                },
                "social": {
                    "synth": _first_sentence(track.summary),
                    "reason": track.summary or "",
                    "hot": social_hot,
                    "signals": signals,
                    "stats": social_stats,
                },
            })

    return {
        "catalogue": {"id": catalogue_db_id, "name": catalogue_name},
        "tracks": result_tracks,
    }


def _process_catalogue_sync(job_id: int, csv_path: str, name: str) -> None:
    db = Database()
    try:
        _update_job(job_id, status="loading", pct=2, agent="loader",
                    step="Loading catalogue · resolving tracks")
        catalog = load_catalog_from_csv(csv_path, db)

        with db.session() as s:
            cat = s.query(Catalog).filter_by(id=catalog.id).one()
            cat.name = name
            s.commit()

        _update_job(job_id, catalogue_id=catalog.id, pct=5)

        with db.session() as s:
            tracks = s.query(Track).filter_by(catalog_id=catalog.id).all()
            track_ids = [t.id for t in tracks]
            artist_ids = list({t.artist_id for t in tracks})

        _update_job(job_id, track_count=len(track_ids))

        # Track agents: 5% → 80%
        track_total = len(track_ids) * len(TRACK_AGENT_NAMES)
        done = 0
        for track_id in track_ids:
            for agent_name in TRACK_AGENT_NAMES:
                pct = 5 + int(75 * done / max(track_total, 1))
                _update_job(job_id, status="analyzing", pct=pct,
                            agent=agent_name,
                            step=_AGENT_LABEL.get(agent_name, agent_name))
                try:
                    run_track_agent(agent_name, track_id)
                except Exception as exc:
                    logger.warning("Agent %s failed for track %s: %s",
                                   agent_name, track_id, exc)
                done += 1

        # Artist agents: 80% → 97%
        artist_total = len(artist_ids) * len(ARTIST_AGENT_NAMES)
        done_a = 0
        for artist_id in artist_ids:
            for agent_name in ARTIST_AGENT_NAMES:
                pct = 80 + int(17 * done_a / max(artist_total, 1))
                _update_job(job_id, pct=pct,
                            agent=agent_name,
                            step=_AGENT_LABEL.get(agent_name, agent_name))
                try:
                    run_artist_agent(agent_name, artist_id)
                except Exception as exc:
                    logger.warning("Agent %s failed for artist %s: %s",
                                   agent_name, artist_id, exc)
                done_a += 1

        _update_job(job_id, status="done", pct=100, agent="rank_and_flag",
                    step="Ranking · flagging top tracks")

    except Exception as exc:
        logger.error("Catalogue pipeline failed for job %s: %s",
                     job_id, exc, exc_info=True)
        _update_job(job_id, status="error", error=str(exc))
    finally:
        try:
            os.unlink(csv_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Catalogue endpoints
# ---------------------------------------------------------------------------

@app.post("/api/catalogues")
async def create_catalogue(
    file: UploadFile = File(...),
    name: str = Form(None),
) -> dict:
    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    track_count = max(0, text.count("\n") - 1)

    if not name:
        name = Path(file.filename or "untitled").stem or "Untitled"

    job = _new_job(name, track_count)

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as fh:
        fh.write(content)
        tmp_path = fh.name

    threading.Thread(
        target=_process_catalogue_sync,
        args=(job.job_id, tmp_path, name),
        daemon=True,
    ).start()

    return {
        "id": job.job_id,
        "name": name,
        "track_count": track_count,
        "status": "pending",
    }


@app.get("/api/catalogues/{catalogue_id}/status")
def get_catalogue_status(catalogue_id: int) -> dict:
    job = _jobs.get(catalogue_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": catalogue_id,
        "status": job.status,
        "pct": job.pct,
        "agent": job.agent,
        "step": job.step,
        "error": job.error,
    }


@app.get("/api/catalogues/{catalogue_id}/results")
def get_catalogue_results(catalogue_id: int) -> dict:
    job = _jobs.get(catalogue_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == "error":
        raise HTTPException(status_code=500, detail=job.error or "Processing failed")
    if job.status != "done" or job.catalogue_id is None:
        raise HTTPException(status_code=202, detail="Processing not complete")
    return _build_results(job.catalogue_id, job.name)


# Serve the frontend — must come last so API routes take precedence
_web_dir = Path(__file__).parent / "catalyst-web"
if _web_dir.is_dir():
    app.mount("/", StaticFiles(directory=_web_dir, html=True), name="static")
