"""
================================================================================
Catalogue Events
================================================================================

The following functions can be used to compile a dataset with catalogue artist
birthdays and release anniversaries using MusicBrainz API

File structure:

* get_artist_birthdays
    Given a query, it returns the birthday of the best match of the search.
* get_releases
    Given a query, it returns every release of the best match (they contain
    a "first_release" field).
* _get
    A convenient GET request template that take into account rate limits.

Notes:
* Rate limit: 1 req/sec without auth, ~5/sec with User-Agent header.
"""

import datetime
import time

import requests

MUSICBRAINZ_BASE = "https://musicbrainz.org/ws/2"
# TODO: An email should be specified via CLI and appended to the User-Agent
#       field wrapped in parentheses, so that MusicBrainz can reach out if
#       rate limits are exceeded. Without it, requests may be throttled or
#       banned.
HEADERS = {
    "User-Agent": "Catalyst/0.1",
    "Accept": "application/json",
}
# Seconds between requests (guaranteed from the API)
RATE_LIMIT = 0.5


# ==============================================================================
# Artist Birthdays
# ==============================================================================
def get_artist_birthday(query: str) -> dict | None:
    """Format: YYY-MM-DD"""
    data = _get("artist", {"query": query, "limit": 5})
    best_match = data.get("artists", [{}])[0]
    return best_match.get("life-span", {}).get("begin")


# ==============================================================================
# Release Anniversary
# ==============================================================================
def get_releases(query: str, limit: int = 100) -> list[dict]:
    data = _get("artist", {"query": query, "limit": 5})
    best_match = data.get("artists", [{}])[0]
    artist_mbid = best_match["id"]

    releases = {}
    for kind in ["album", "single", "ep"]:
        data = _get(
            "release-group",
            {
                "artist": artist_mbid,
                "type": kind,
                "limit": limit,
            },
        )
        releases[kind] = [
            {
                "id": release["id"],
                "title": release["title"],
                "type": release.get("primary-type", kind),
                "first_release": release.get("first-release-date", None),
            }
            for release in data.get("release-groups", [])
        ]

    return releases


# ==============================================================================
# Module-Private Functions
# ==============================================================================
def _get(endpoint: str, params: dict) -> dict:
    """GET wrapper with rate limiting."""
    params["fmt"] = "json"
    resp = requests.get(
        f"{MUSICBRAINZ_BASE}/{endpoint}", params=params, headers=HEADERS
    )
    resp.raise_for_status()
    time.sleep(RATE_LIMIT)
    return resp.json()
