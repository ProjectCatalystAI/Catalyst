"""Catalyst analyzer agents (Strands-agents).

Public surface:
- Track agents:  `run_track_agent`, `TRACK_AGENT_REGISTRY`, `TRACK_AGENT_NAMES`
- Artist agents: `run_artist_agent`, `ARTIST_AGENT_REGISTRY`, `ARTIST_AGENT_NAMES`
"""

from src.agents.runner import (
    ARTIST_AGENT_NAMES,
    ARTIST_AGENT_REGISTRY,
    TRACK_AGENT_NAMES,
    TRACK_AGENT_REGISTRY,
    run_artist_agent,
    run_track_agent,
)

__all__ = [
    "run_track_agent",
    "TRACK_AGENT_REGISTRY",
    "TRACK_AGENT_NAMES",
    "run_artist_agent",
    "ARTIST_AGENT_REGISTRY",
    "ARTIST_AGENT_NAMES",
]
