"""Instagram analyzer agents."""

from __future__ import annotations

from strands import Agent

from src.agents.model import make_model
from src.agents.prompts import (
    INSTAGRAM_ARTIST_HISTORIC_PROMPT,
    INSTAGRAM_ARTIST_PROMPT,
    INSTAGRAM_TRACK_HISTORIC_PROMPT,
    INSTAGRAM_TRACK_PROMPT,
    INSTAGRAM_VIDEO_PROMPT,
)
from src.agents.tools.db_fetch import (
    fetch_instagram_artist_historic,
    fetch_instagram_artist_stats,
    fetch_instagram_track_historic,
    fetch_instagram_track_stats,
    fetch_top5_instagram_videos,
)
from src.agents.tools.video import analyze_video


def instagram_track_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=INSTAGRAM_TRACK_PROMPT,
        tools=[fetch_instagram_track_stats],
    )


def instagram_track_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=INSTAGRAM_TRACK_HISTORIC_PROMPT,
        tools=[fetch_instagram_track_historic],
    )


def instagram_video_analyzer() -> Agent:
    return Agent(
        model=make_model(max_tokens=3000),
        system_prompt=INSTAGRAM_VIDEO_PROMPT,
        tools=[fetch_top5_instagram_videos, analyze_video],
    )


def instagram_artist_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=INSTAGRAM_ARTIST_PROMPT,
        tools=[fetch_instagram_artist_stats],
    )


def instagram_artist_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=INSTAGRAM_ARTIST_HISTORIC_PROMPT,
        tools=[fetch_instagram_artist_historic],
    )
