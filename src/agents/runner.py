"""Agent execution + DB writeback.

Each entry in TRACK_AGENT_REGISTRY is a callable `(track_id: int) -> str` and
each entry in ARTIST_AGENT_REGISTRY is a callable `(artist_id: int) -> str`.
Both flavours:
1. Build the right agent.
2. Run it with a fixed user prompt.
3. Persist the resulting analysis to the appropriate column(s).
4. Return the raw analysis text (or a JSON string for video agents).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Callable

from strands import Agent

from src.agents.instagram import (
    instagram_artist_analyzer,
    instagram_artist_historic_analyzer,
    instagram_track_analyzer,
    instagram_track_historic_analyzer,
    instagram_video_analyzer,
)
from src.agents.period import period_track_analyzer
from src.agents.spotify import (
    spotify_artist_analyzer,
    spotify_artist_historic_analyzer,
    spotify_track_analyzer,
    spotify_track_historic_analyzer,
)
from src.agents.summarizer import artist_summarizer, track_summarizer
from src.agents.tiktok import (
    tiktok_artist_analyzer,
    tiktok_artist_historic_analyzer,
    tiktok_track_analyzer,
    tiktok_track_historic_analyzer,
    tiktok_video_analyzer,
)
from src.agents.youtube import (
    youtube_artist_analyzer,
    youtube_artist_historic_analyzer,
    youtube_shorts_analyzer,
    youtube_track_analyzer,
    youtube_track_historic_analyzer,
    youtube_video_analyzer,
)
from src.db import (
    Artist,
    Database,
    InstagramArtist,
    InstagramArtistHistoric,
    InstagramTrack,
    InstagramTrackHistoric,
    InstagramVideoTrack,
    SpotifyArtist,
    SpotifyArtistHistoric,
    SpotifyTrack,
    SpotifyTrackHistoric,
    TiktokArtist,
    TiktokArtistHistoric,
    TiktokTrack,
    TiktokTrackHistoric,
    TiktokVideoTrack,
    Track,
    YoutubeArtist,
    YoutubeArtistHistoric,
    YoutubeShortTrack,
    YoutubeTrack,
    YoutubeTrackHistoric,
    YoutubeVideoTrack,
)

logger = logging.getLogger(__name__)

_db = Database()


def _run(agent: Agent, entity_id: int, entity_name: str = "track") -> str:
    response = agent(f"Analyze the data for {entity_name}_id={entity_id}.")
    return str(response).strip()


def _parse_video_map(text: str) -> dict[str, str]:
    """Extract the JSON {id: analysis} returned by a video analyzer.

    The agent may wrap the JSON in fences or include incidental whitespace.
    """
    candidate = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    else:
        first = candidate.find("{")
        last = candidate.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = candidate[first : last + 1]
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        logger.warning("Could not parse video analyzer JSON: %s", text[:200])
        return {}
    return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}


# ---------------------------------------------------------------------------
# Persistence helpers — one per agent
# ---------------------------------------------------------------------------
def _persist_simple(model_cls, track_id: int, analysis: str) -> None:
    with _db.session() as s:
        row = s.query(model_cls).filter_by(track_id=track_id).one_or_none()
        if row is None:
            logger.warning(
                "No %s row for track_id=%s; skipping persistence",
                model_cls.__tablename__,
                track_id,
            )
            return
        row.analysis = analysis
        s.commit()


def _persist_historic_latest(model_cls, track_id: int, analysis: str) -> None:
    with _db.session() as s:
        row = (
            s.query(model_cls)
            .filter_by(track_id=track_id)
            .order_by(model_cls.date.desc())
            .first()
        )
        if row is None:
            logger.warning(
                "No %s row for track_id=%s; skipping persistence",
                model_cls.__tablename__,
                track_id,
            )
            return
        row.analysis = analysis
        s.commit()


def _persist_video_map(model_cls, video_analyses: dict[str, str]) -> None:
    if not video_analyses:
        return
    with _db.session() as s:
        for raw_id, text in video_analyses.items():
            try:
                row_id = int(raw_id)
            except (TypeError, ValueError):
                continue
            row = s.query(model_cls).filter_by(id=row_id).one_or_none()
            if row is None:
                logger.warning(
                    "No %s row id=%s; skipping", model_cls.__tablename__, row_id
                )
                continue
            row.analysis = text
        s.commit()


# ---------------------------------------------------------------------------
# Per-agent runners
# ---------------------------------------------------------------------------
def _run_spotify_track(track_id: int) -> str:
    text = _run(spotify_track_analyzer(), track_id)
    _persist_simple(SpotifyTrack, track_id, text)
    return text


def _run_spotify_track_historic(track_id: int) -> str:
    text = _run(spotify_track_historic_analyzer(), track_id)
    _persist_historic_latest(SpotifyTrackHistoric, track_id, text)
    return text


def _run_instagram_track(track_id: int) -> str:
    text = _run(instagram_track_analyzer(), track_id)
    _persist_simple(InstagramTrack, track_id, text)
    return text


def _run_instagram_track_historic(track_id: int) -> str:
    text = _run(instagram_track_historic_analyzer(), track_id)
    _persist_historic_latest(InstagramTrackHistoric, track_id, text)
    return text


def _run_instagram_video(track_id: int) -> str:
    text = _run(instagram_video_analyzer(), track_id)
    _persist_video_map(InstagramVideoTrack, _parse_video_map(text))
    return text


def _run_tiktok_track(track_id: int) -> str:
    text = _run(tiktok_track_analyzer(), track_id)
    _persist_simple(TiktokTrack, track_id, text)
    return text


def _run_tiktok_track_historic(track_id: int) -> str:
    text = _run(tiktok_track_historic_analyzer(), track_id)
    _persist_historic_latest(TiktokTrackHistoric, track_id, text)
    return text


def _run_tiktok_video(track_id: int) -> str:
    text = _run(tiktok_video_analyzer(), track_id)
    _persist_video_map(TiktokVideoTrack, _parse_video_map(text))
    return text


def _run_youtube_track(track_id: int) -> str:
    text = _run(youtube_track_analyzer(), track_id)
    _persist_simple(YoutubeTrack, track_id, text)
    return text


def _run_youtube_track_historic(track_id: int) -> str:
    text = _run(youtube_track_historic_analyzer(), track_id)
    _persist_historic_latest(YoutubeTrackHistoric, track_id, text)
    return text


def _run_youtube_video(track_id: int) -> str:
    text = _run(youtube_video_analyzer(), track_id)
    _persist_video_map(YoutubeVideoTrack, _parse_video_map(text))
    return text


def _run_youtube_shorts(track_id: int) -> str:
    text = _run(youtube_shorts_analyzer(), track_id)
    _persist_video_map(YoutubeShortTrack, _parse_video_map(text))
    return text


def _run_period_track(track_id: int) -> str:
    return _run(period_track_analyzer(), track_id)


def _run_track_summarizer(track_id: int) -> str:
    text = _run(track_summarizer(), track_id)
    with _db.session() as s:
        row = s.query(Track).filter_by(id=track_id).one_or_none()
        if row is None:
            logger.warning("No track row id=%s; skipping summary save", track_id)
            return text
        row.summary = text
        s.commit()
    return text


TRACK_AGENT_REGISTRY: dict[str, Callable[[int], str]] = {
    "spotify_track": _run_spotify_track,
    "spotify_track_historic": _run_spotify_track_historic,
    "instagram_track": _run_instagram_track,
    "instagram_track_historic": _run_instagram_track_historic,
    "instagram_video": _run_instagram_video,
    "tiktok_track": _run_tiktok_track,
    "tiktok_track_historic": _run_tiktok_track_historic,
    "tiktok_video": _run_tiktok_video,
    "youtube_track": _run_youtube_track,
    "youtube_track_historic": _run_youtube_track_historic,
    "youtube_video": _run_youtube_video,
    "youtube_shorts": _run_youtube_shorts,
    "period_track": _run_period_track,
    "track_summarizer": _run_track_summarizer,
}

TRACK_AGENT_NAMES = tuple(TRACK_AGENT_REGISTRY.keys())


def run_track_agent(name: str, track_id: int) -> str:
    if name not in TRACK_AGENT_REGISTRY:
        raise ValueError(
            f"Unknown track agent {name!r}. "
            f"Available: {', '.join(TRACK_AGENT_NAMES)}"
        )
    return TRACK_AGENT_REGISTRY[name](track_id)


# ===========================================================================
# Artist (profile) — persistence helpers, runners, registry
# ===========================================================================
def _persist_artist_simple(model_cls, artist_id: int, analysis: str) -> None:
    with _db.session() as s:
        row = s.query(model_cls).filter_by(artist_id=artist_id).one_or_none()
        if row is None:
            logger.warning(
                "No %s row for artist_id=%s; skipping persistence",
                model_cls.__tablename__,
                artist_id,
            )
            return
        row.analysis = analysis
        s.commit()


def _persist_artist_historic_latest(model_cls, artist_id: int, analysis: str) -> None:
    with _db.session() as s:
        row = (
            s.query(model_cls)
            .filter_by(artist_id=artist_id)
            .order_by(model_cls.date.desc())
            .first()
        )
        if row is None:
            logger.warning(
                "No %s row for artist_id=%s; skipping persistence",
                model_cls.__tablename__,
                artist_id,
            )
            return
        row.analysis = analysis
        s.commit()


def _run_spotify_artist(artist_id: int) -> str:
    text = _run(spotify_artist_analyzer(), artist_id, "artist")
    _persist_artist_simple(SpotifyArtist, artist_id, text)
    return text


def _run_spotify_artist_historic(artist_id: int) -> str:
    text = _run(spotify_artist_historic_analyzer(), artist_id, "artist")
    _persist_artist_historic_latest(SpotifyArtistHistoric, artist_id, text)
    return text


def _run_instagram_artist(artist_id: int) -> str:
    text = _run(instagram_artist_analyzer(), artist_id, "artist")
    _persist_artist_simple(InstagramArtist, artist_id, text)
    return text


def _run_instagram_artist_historic(artist_id: int) -> str:
    text = _run(instagram_artist_historic_analyzer(), artist_id, "artist")
    _persist_artist_historic_latest(InstagramArtistHistoric, artist_id, text)
    return text


def _run_tiktok_artist(artist_id: int) -> str:
    text = _run(tiktok_artist_analyzer(), artist_id, "artist")
    _persist_artist_simple(TiktokArtist, artist_id, text)
    return text


def _run_tiktok_artist_historic(artist_id: int) -> str:
    text = _run(tiktok_artist_historic_analyzer(), artist_id, "artist")
    _persist_artist_historic_latest(TiktokArtistHistoric, artist_id, text)
    return text


def _run_youtube_artist(artist_id: int) -> str:
    text = _run(youtube_artist_analyzer(), artist_id, "artist")
    _persist_artist_simple(YoutubeArtist, artist_id, text)
    return text


def _run_youtube_artist_historic(artist_id: int) -> str:
    text = _run(youtube_artist_historic_analyzer(), artist_id, "artist")
    _persist_artist_historic_latest(YoutubeArtistHistoric, artist_id, text)
    return text


def _run_artist_summarizer(artist_id: int) -> str:
    text = _run(artist_summarizer(), artist_id, "artist")
    with _db.session() as s:
        row = s.query(Artist).filter_by(id=artist_id).one_or_none()
        if row is None:
            logger.warning(
                "No artist row id=%s; skipping summary save", artist_id
            )
            return text
        row.analysis = text
        s.commit()
    return text


ARTIST_AGENT_REGISTRY: dict[str, Callable[[int], str]] = {
    "spotify_artist": _run_spotify_artist,
    "spotify_artist_historic": _run_spotify_artist_historic,
    "instagram_artist": _run_instagram_artist,
    "instagram_artist_historic": _run_instagram_artist_historic,
    "tiktok_artist": _run_tiktok_artist,
    "tiktok_artist_historic": _run_tiktok_artist_historic,
    "youtube_artist": _run_youtube_artist,
    "youtube_artist_historic": _run_youtube_artist_historic,
    "artist_summarizer": _run_artist_summarizer,
}

ARTIST_AGENT_NAMES = tuple(ARTIST_AGENT_REGISTRY.keys())


def run_artist_agent(name: str, artist_id: int) -> str:
    if name not in ARTIST_AGENT_REGISTRY:
        raise ValueError(
            f"Unknown artist agent {name!r}. "
            f"Available: {', '.join(ARTIST_AGENT_NAMES)}"
        )
    return ARTIST_AGENT_REGISTRY[name](artist_id)
