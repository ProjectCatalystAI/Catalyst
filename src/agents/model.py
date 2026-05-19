"""Shared model factory for all Catalyst agents.

Uses Featherless (https://featherless.ai) — an OpenAI-compatible inference
endpoint — with the multimodal moonshotai/Kimi-K2.6 model.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from strands.models.openai import OpenAIModel

load_dotenv()

FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"
MODEL_ID = "moonshotai/Kimi-K2.6"


def make_model(
    temperature: float = 0.6,
    top_p: int = 1,
    top_k: int = -1,
    max_tokens: int | None = None,
) -> OpenAIModel:
    api_key = os.environ.get("FEATHERLESS_API_KEY")
    if not api_key:
        raise RuntimeError("FEATHERLESS_API_KEY is not set in the environment")
    params: dict = {
        "temperature": temperature,
        "top_p": top_p,
        "extra_body": {"top_k": top_k},
    }
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
    return OpenAIModel(
        client_args={"api_key": api_key, "base_url": FEATHERLESS_BASE_URL},
        model_id=MODEL_ID,
        params=params,
    )
