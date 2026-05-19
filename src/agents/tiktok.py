"""TikTok analyzer agents."""

from __future__ import annotations

from strands import Agent

from src.agents.model import make_model
from src.agents.prompts import (
    TIKTOK_ARTIST_HISTORIC_PROMPT,
    TIKTOK_ARTIST_PROMPT,
    TIKTOK_TRACK_HISTORIC_PROMPT,
    TIKTOK_TRACK_PROMPT,
    TIKTOK_VIDEO_PROMPT,
)
from src.agents.tools.db_fetch import (
    fetch_tiktok_artist_historic,
    fetch_tiktok_artist_stats,
    fetch_tiktok_track_historic,
    fetch_tiktok_track_stats,
    fetch_top5_tiktok_videos,
)
from src.agents.tools.video import analyze_video


def tiktok_track_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=TIKTOK_TRACK_PROMPT,
        tools=[fetch_tiktok_track_stats],
    )


def tiktok_track_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=TIKTOK_TRACK_HISTORIC_PROMPT,
        tools=[fetch_tiktok_track_historic],
    )


def tiktok_video_analyzer() -> Agent:
    return Agent(
        model=make_model(max_tokens=3000),
        system_prompt=TIKTOK_VIDEO_PROMPT,
        tools=[fetch_top5_tiktok_videos, analyze_video],
    )


def tiktok_artist_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=TIKTOK_ARTIST_PROMPT,
        tools=[fetch_tiktok_artist_stats],
    )


def tiktok_artist_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=TIKTOK_ARTIST_HISTORIC_PROMPT,
        tools=[fetch_tiktok_artist_historic],
    )
