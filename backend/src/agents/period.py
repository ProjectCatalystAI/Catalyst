"""Period Track Analyzer agent — calendar-context strategic timing advice."""

from __future__ import annotations

from strands import Agent

from src.agents.model import make_model
from src.agents.prompts import PERIOD_TRACK_PROMPT
from src.agents.tools.period import (
    calendar_anchors,
    fetch_track_basics,
    today_info,
)


def period_track_analyzer() -> Agent:
    return Agent(
        model=make_model(),
        system_prompt=PERIOD_TRACK_PROMPT,
        tools=[fetch_track_basics, today_info, calendar_anchors],
    )
