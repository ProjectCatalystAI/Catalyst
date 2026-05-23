"""Video download + multimodal description pipeline.

Downloads a video from any supported URL (Instagram Reels, TikTok, YouTube,
YouTube Shorts) via yt-dlp, samples N frames using ffmpeg, and asks an
OpenRouter-hosted multimodal model to describe the content.

The CLI tools `yt-dlp` and `ffmpeg` are expected to be on PATH.
"""

from __future__ import annotations

import base64
import logging
import os
import random
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

from src.agents.model import OPENROUTER_BASE_URL, VIDEO_MODEL_ID

load_dotenv()
logger = logging.getLogger(__name__)

NUM_FRAMES = 8
RATE_LIMIT_MAX_RETRIES = 12
RATE_LIMIT_BASE_DELAY = 2.0
RATE_LIMIT_MAX_DELAY = 60.0
POST_CALL_SETTLE_SECONDS = 1.0

YTDLP_IMPERSONATE = os.environ.get("YTDLP_IMPERSONATE", "chrome")
YTDLP_COOKIES_FROM_BROWSER = os.environ.get("YTDLP_COOKIES_FROM_BROWSER", "chrome")

_video_call_lock = threading.Lock()


def _download(url: str, workdir: Path) -> Path:
    out_template = str(workdir / "video.%(ext)s")
    cmd = [
        "yt-dlp",
        "--no-warnings",
        "--quiet",
        "-f", "mp4/best[ext=mp4]/best",
        "-o", out_template,
    ]
    if YTDLP_IMPERSONATE:
        cmd += ["--impersonate", YTDLP_IMPERSONATE]
    if YTDLP_COOKIES_FROM_BROWSER:
        cmd += ["--cookies-from-browser", YTDLP_COOKIES_FROM_BROWSER]
    cmd.append(url)
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
    for child in workdir.iterdir():
        if child.is_file() and child.stem == "video":
            return child
    raise RuntimeError("yt-dlp did not produce a file")


def _extract_frames(video_path: Path, workdir: Path, n: int = NUM_FRAMES) -> list[Path]:
    pattern = str(workdir / "frame_%03d.jpg")
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(video_path),
        "-vf", f"thumbnail,fps=1/2",
        "-frames:v", str(n),
        "-q:v", "3",
        pattern,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=120)
    frames = sorted(workdir.glob("frame_*.jpg"))
    if not frames:
        raise RuntimeError("ffmpeg did not produce any frames")
    return frames[:n]


def _describe_with_video_model(frames: list[Path]) -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    content: list[dict] = [
        {
            "type": "text",
            "text": (
                "These frames are sampled evenly from a single short-form "
                "music-related video. Describe the video content in 2-4 "
                "sentences: what is shown, the mood, any text overlays, and "
                "how the music seems to be used. Be specific and concise."
            ),
        }
    ]
    for f in frames:
        b64 = base64.b64encode(f.read_bytes()).decode("ascii")
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            }
        )

    body = {
        "model": VIDEO_MODEL_ID,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 1200,
        "temperature": 0.3,
        "provider": {"sort": "throughput"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    with _video_call_lock:
        try:
            for attempt in range(RATE_LIMIT_MAX_RETRIES + 1):
                try:
                    resp = requests.post(
                        f"{OPENROUTER_BASE_URL}/chat/completions",
                        headers=headers,
                        json=body,
                        timeout=180,
                    )
                except (requests.ConnectionError, requests.Timeout) as e:
                    if attempt >= RATE_LIMIT_MAX_RETRIES:
                        raise
                    delay = min(
                        RATE_LIMIT_MAX_DELAY,
                        RATE_LIMIT_BASE_DELAY * (2**attempt),
                    )
                    delay += random.uniform(0, delay * 0.25)
                    logger.info(
                        "OpenRouter network error on attempt %d/%d (%s); "
                        "sleeping %.1fs before retry",
                        attempt + 1,
                        RATE_LIMIT_MAX_RETRIES,
                        e.__class__.__name__,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                if resp.status_code in (429, 503) and attempt < RATE_LIMIT_MAX_RETRIES:
                    retry_after = resp.headers.get("Retry-After")
                    try:
                        delay = float(retry_after) if retry_after is not None else None
                    except ValueError:
                        delay = None
                    if delay is None:
                        delay = min(
                            RATE_LIMIT_MAX_DELAY,
                            RATE_LIMIT_BASE_DELAY * (2**attempt),
                        )
                        delay += random.uniform(0, delay * 0.25)
                    logger.info(
                        "OpenRouter %s on attempt %d/%d; sleeping %.1fs before retry",
                        resp.status_code,
                        attempt + 1,
                        RATE_LIMIT_MAX_RETRIES,
                        delay,
                    )
                    time.sleep(delay)
                    continue

                resp.raise_for_status()
                payload = resp.json()
                message = payload["choices"][0]["message"]
                text = (message.get("content") or "").strip()
                if not text:
                    text = (message.get("reasoning") or "").strip()
                if not text:
                    raise RuntimeError("OpenRouter returned an empty description")
                return text

            raise RuntimeError("unreachable")
        finally:
            time.sleep(POST_CALL_SETTLE_SECONDS)


def describe_video(url: str) -> str:
    """Download a video and return a 2-4 sentence description.

    On failure (download error, no frames, model error) returns a string
    starting with `unavailable:` so callers can include it in analyses without
    crashing the agent run.
    """
    workdir = Path(tempfile.mkdtemp(prefix="catalyst_video_"))
    try:
        try:
            video_path = _download(url, workdir)
        except subprocess.CalledProcessError as e:
            logger.warning("yt-dlp failed for %s: %s", url, e.stderr)
            return f"unavailable: download failed ({url})"
        except subprocess.TimeoutExpired:
            return f"unavailable: download timed out ({url})"

        try:
            frames = _extract_frames(video_path, workdir)
        except subprocess.CalledProcessError as e:
            logger.warning("ffmpeg failed for %s: %s", url, e.stderr)
            return f"unavailable: frame extraction failed ({url})"

        try:
            return _describe_with_video_model(frames)
        except Exception as e:
            logger.warning("Video model description failed for %s: %s", url, e)
            return f"unavailable: model error ({url})"
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
