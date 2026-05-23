"""Shared model factory for all Catalyst agents.

Uses OpenRouter (https://openrouter.ai) — an OpenAI-compatible inference
endpoint — with Gemini 3.1 Flash Lite for text reasoning and synthesis.
Video understanding uses a separate multimodal model (see `video_pipeline.py`).
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from strands.models.openai import OpenAIModel

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_ID = "google/gemini-3.1-flash-lite"
# MODEL_IDE = "nvidia/nemotron-3-super-120b-a12b:free"
VIDEO_MODEL_ID = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"


def make_model(
    temperature: float = 0.6,
    top_p: int = 1,
    top_k: int = -1,
    max_tokens: int | None = None,
) -> OpenAIModel:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the environment")
    params: dict = {
        "temperature": temperature,
        "top_p": top_p,
        "extra_body": {
            "top_k": top_k,
            "provider": {"sort": "throughput"},
        },
    }
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
    return OpenAIModel(
        client_args={"api_key": api_key, "base_url": OPENROUTER_BASE_URL},
        model_id=MODEL_ID,
        params=params,
    )
