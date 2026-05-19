"""Track and Artist Summarizers — consolidate every per-platform analysis."""

from __future__ import annotations

from strands import Agent

from src.agents.model import make_model
from src.agents.prompts import ARTIST_SUMMARIZER_PROMPT, SUMMARIZER_PROMPT
from src.agents.tools.db_fetch import fetch_all_analyses, fetch_all_artist_analyses


def track_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=2500),
        system_prompt=SUMMARIZER_PROMPT,
        tools=[fetch_all_analyses],
    )


def artist_summarizer() -> Agent:
    return Agent(
        model=make_model(max_tokens=2500),
        system_prompt=ARTIST_SUMMARIZER_PROMPT,
        tools=[fetch_all_artist_analyses],
    )
