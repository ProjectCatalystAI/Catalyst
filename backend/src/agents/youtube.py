"""YouTube analyzer agents (Track, Historic, Video, Shorts, Artist)."""

from __future__ import annotations

from strands import Agent

from src.agents.model import make_model
from src.agents.prompts import (
    YOUTUBE_ARTIST_HISTORIC_PROMPT,
    YOUTUBE_ARTIST_PROMPT,
    YOUTUBE_SHORTS_PROMPT,
    YOUTUBE_TRACK_HISTORIC_PROMPT,
    YOUTUBE_TRACK_PROMPT,
    YOUTUBE_VIDEO_PROMPT,
)
from src.agents.tools.db_fetch import (
    fetch_top5_youtube_shorts,
    fetch_top5_youtube_videos,
    fetch_youtube_artist_historic,
    fetch_youtube_artist_stats,
    fetch_youtube_track_historic,
    fetch_youtube_track_stats,
)
from src.agents.tools.video import analyze_video


def youtube_track_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=YOUTUBE_TRACK_PROMPT,
        tools=[fetch_youtube_track_stats],
    )


def youtube_track_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=YOUTUBE_TRACK_HISTORIC_PROMPT,
        tools=[fetch_youtube_track_historic],
    )


def youtube_video_analyzer() -> Agent:
    return Agent(
        model=make_model(max_tokens=3000),
        system_prompt=YOUTUBE_VIDEO_PROMPT,
        tools=[fetch_top5_youtube_videos, analyze_video],
    )


def youtube_shorts_analyzer() -> Agent:
    return Agent(
        model=make_model(max_tokens=3000),
        system_prompt=YOUTUBE_SHORTS_PROMPT,
        tools=[fetch_top5_youtube_shorts, analyze_video],
    )


def youtube_artist_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=YOUTUBE_ARTIST_PROMPT,
        tools=[fetch_youtube_artist_stats],
    )


def youtube_artist_historic_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=YOUTUBE_ARTIST_HISTORIC_PROMPT,
        tools=[fetch_youtube_artist_historic],
    )
