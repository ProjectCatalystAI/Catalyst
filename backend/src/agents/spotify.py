"""Spotify analyzer agents."""

from __future__ import annotations

from strands import Agent

from src.agents.model import make_model
from src.agents.prompts import (
    SPOTIFY_ARTIST_HISTORIC_PROMPT,
    SPOTIFY_ARTIST_PROMPT,
    SPOTIFY_TRACK_HISTORIC_PROMPT,
    SPOTIFY_TRACK_PROMPT,
)
from src.agents.tools.db_fetch import (
    fetch_spotify_artist_historic,
    fetch_spotify_artist_stats,
    fetch_spotify_track_historic,
    fetch_spotify_track_stats,
)


def spotify_track_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=SPOTIFY_TRACK_PROMPT,
        tools=[fetch_spotify_track_stats],
    )


def spotify_track_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=SPOTIFY_TRACK_HISTORIC_PROMPT,
        tools=[fetch_spotify_track_historic],
    )


def spotify_artist_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=SPOTIFY_ARTIST_PROMPT,
        tools=[fetch_spotify_artist_stats],
    )


def spotify_artist_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=SPOTIFY_ARTIST_HISTORIC_PROMPT,
        tools=[fetch_spotify_artist_historic],
    )
