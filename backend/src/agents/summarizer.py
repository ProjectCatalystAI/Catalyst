"""Track and Artist Summarizers — consolidate every per-platform analysis."""

from __future__ import annotations

from strands import Agent

from src.agents.model import make_model
from src.agents.prompts import (
    ARTIST_SUMMARIZER_PROMPT,
    INSTAGRAM_SOURCE_SUMMARIZER_PROMPT,
    SPOTIFY_SOURCE_SUMMARIZER_PROMPT,
    SUMMARIZER_PROMPT,
    TIKTOK_SOURCE_SUMMARIZER_PROMPT,
    YOUTUBE_SOURCE_SUMMARIZER_PROMPT,
)
from src.agents.tools.db_fetch import (
    fetch_all_analyses,
    fetch_all_artist_analyses,
    fetch_instagram_analyses,
    fetch_spotify_analyses,
    fetch_tiktok_analyses,
    fetch_youtube_analyses,
)


def track_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=2500),
        system_prompt=SUMMARIZER_PROMPT,
        tools=[fetch_all_analyses],
    )


def spotify_track_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=600),
        system_prompt=SPOTIFY_SOURCE_SUMMARIZER_PROMPT,
        tools=[fetch_spotify_analyses],
    )


def instagram_track_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=600),
        system_prompt=INSTAGRAM_SOURCE_SUMMARIZER_PROMPT,
        tools=[fetch_instagram_analyses],
    )


def tiktok_track_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=600),
        system_prompt=TIKTOK_SOURCE_SUMMARIZER_PROMPT,
        tools=[fetch_tiktok_analyses],
    )


def youtube_track_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=600),
        system_prompt=YOUTUBE_SOURCE_SUMMARIZER_PROMPT,
        tools=[fetch_youtube_analyses],
    )


def artist_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=2500),
        system_prompt=ARTIST_SUMMARIZER_PROMPT,
        tools=[fetch_all_artist_analyses],
    )
