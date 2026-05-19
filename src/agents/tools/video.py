"""Strands `@tool` wrapper around the video description pipeline."""

from __future__ import annotations

from strands import tool

from src.agents.video_pipeline import describe_video


@tool
def analyze_video(url: str) -> str:
    """Download a video from the given URL and return a 2-4 sentence description.

    Supports Instagram Reels, TikTok, YouTube, and YouTube Shorts URLs. On any
    failure returns a string starting with `unavailable:` instead of raising.
    """
    return describe_video(url)
