"""FastAPI surface for the Catalyst analyzer suite.

Run with:
    uvicorn src.api:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.agents.runner import (
    ARTIST_AGENT_NAMES,
    TRACK_AGENT_NAMES,
    run_artist_agent,
    run_track_agent,
)

app = FastAPI(title="Catalyst Analyzers")


class AnalyzeTrackRequest(BaseModel):
    track_id: int = Field(..., description="Primary key of the target track row.")
    agents: list[str] = Field(
        ...,
        description=(
            "Ordered list of analyzer names to invoke. Each name must be one of: "
            + ", ".join(TRACK_AGENT_NAMES)
        ),
    )


class AnalyzeTrackResponse(BaseModel):
    track_id: int
    results: dict[str, str]


class AnalyzeArtistRequest(BaseModel):
    artist_id: int = Field(..., description="Primary key of the target artist row.")
    agents: list[str] = Field(
        ...,
        description=(
            "Ordered list of profile analyzer names to invoke. Each name must "
            "be one of: " + ", ".join(ARTIST_AGENT_NAMES)
        ),
    )


class AnalyzeArtistResponse(BaseModel):
    artist_id: int
    results: dict[str, str]


@app.get("/track-agents")
def list_track_agents() -> dict:
    return {"agents": list(TRACK_AGENT_NAMES)}


@app.get("/artist-agents")
def list_artist_agents() -> dict:
    return {"agents": list(ARTIST_AGENT_NAMES)}


@app.post("/analyze-track", response_model=AnalyzeTrackResponse)
def analyze_track(req: AnalyzeTrackRequest) -> AnalyzeTrackResponse:
    unknown = [a for a in req.agents if a not in TRACK_AGENT_NAMES]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agents: {unknown}. Valid: {list(TRACK_AGENT_NAMES)}",
        )
    results: dict[str, str] = {}
    for name in req.agents:
        results[name] = run_track_agent(name, req.track_id)
    return AnalyzeTrackResponse(track_id=req.track_id, results=results)


@app.post("/analyze-artist", response_model=AnalyzeArtistResponse)
def analyze_artist(req: AnalyzeArtistRequest) -> AnalyzeArtistResponse:
    unknown = [a for a in req.agents if a not in ARTIST_AGENT_NAMES]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agents: {unknown}. Valid: {list(ARTIST_AGENT_NAMES)}",
        )
    results: dict[str, str] = {}
    for name in req.agents:
        results[name] = run_artist_agent(name, req.artist_id)
    return AnalyzeArtistResponse(artist_id=req.artist_id, results=results)
