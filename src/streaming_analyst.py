"""
================================================================================
Streaming Analyst
================================================================================

The following functions can be run by agents using MCP to retrieve information
about artists, tracks, and albums on various DSPs.

File structure:
* Spotify functions
    * get_popularity
      Return the popularity index. Useful to estimate the recent raising of
      popularity of an artist, track, or album.
    * search_spotify_id
      Return the Spotify ID that has to be passed to get_popularity.
* Last.FM functions
    * get_lastfm_info
      Return various information such as playcount, listeners, genres, and
      similar artists.

TODO: If we want to monitor specific artists, tracks, or albums, we could let
      the agent execute these functions periodically (e.g., once a day) to save
      the relevant data into a CSV. It would help to understand how much an
      artist, track, or album is raising (e.g., monitoring the popularity
      index).
TODO: At the end, we could cross-reference all the gathered data.
"""

import os
import time
from typing import Any

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

# ==============================================================================
# Constants Loading
# ==============================================================================
load_dotenv()
SPOTIFY_CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
LASTFM_API_KEY = os.environ["LASTFM_API_KEY"]
LASTFM_API_SECRET = os.environ["LASTFM_API_SECRET"]
LASTFM_BASE = "https://ws.audioscrobbler.com/2.0/"


# ==============================================================================
# AccessToken Class
# ==============================================================================
# A class to conveniently cache the Bearer token needed to send API requests
# to Spotify.
# ------------------------------------------------------------------------------
class AccessToken:
    def __init__(self):
        self._token: str | None = None
        self._token_expiry: float = 0

    def get(self) -> str:
        def _is_expired():
            return time.time() < self._token_expiry - 60

        if self._token is not None and not _is_expired():
            return self._token

        r = requests.post(
            "https://accounts.spotify.com/api/token",
            data={"grant_type": "client_credentials"},
            auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
        )
        r.raise_for_status()
        return r.json()["access_token"]


mcp = FastMCP("streaming-analyst")
token = AccessToken()


# ==============================================================================
# Spotify Functions
# ==============================================================================
@mcp.tool()
def get_popularity(spotify_id: str, kind: str) -> int:
    """
    Get Spotify popularity score (0-100) for a track, artist, or album.

    :param spotify_id: Spotify ID (e.g. '2lTm559tuIvatlT1u0JYG2')
    :param kind: one of 'track', 'artist', 'album'
    :raises ValueError: if kind is invalid
    :raises RuntimeError: if the API call fails
    """
    if kind not in ("track", "artist", "album"):
        raise ValueError(
            f"Invalid kind '{kind}'. Must be 'track', 'artist', or 'album'."
        )

    access_token = token.get()

    url = f"https://api.spotify.com/v1/{kind}s/{spotify_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()["popularity"]


@mcp.tool()
def search_spotify_id(query: str, kind: str) -> str:
    """
    Search for a track/artist/album by name and return its Spotify ID.

    :param query: search string (e.g. 'Purple Rain')
    :param kind: one of 'track', 'artist', 'album'
    :param access_token: valid OAuth access token
    :returns: Spotify ID of the top result
    """
    if kind not in ("track", "artist", "album"):
        raise ValueError(
            f"Invalid kind '{kind}'. Must be 'track', 'artist', or 'album'."
        )

    access_token = token.get()

    r = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"q": query, "type": kind, "limit": 1},
    )
    r.raise_for_status()

    items = r.json()[f"{kind}s"]["items"]
    if not items:
        raise RuntimeError(f"No {kind} found for query '{query}'.")

    return items[0]["id"]


# ==============================================================================
# Last.FM Functions
# ==============================================================================
@mcp.tool()
def get_lastfm_info(
    artist: str, track: str | None = None, album: str | None = None
) -> dict[str, Any]:
    """
    Fetch info for an artist, track, or album from Last.fm.

    Infers the query type from the provided arguments:
    - only artist -> artist info
    - artist + track -> track info
    - artist + album -> album info

    :param artist: The name of the artist.
    :param track: The name of the track (mutually exclusive with album).
    :param album: The name of the album (mutually exclusive with track).
    :returns: A dictionary with 'name', 'listeners', 'playcount', and 'meta'
              (the latter containing 'tags' and 'similar_artist').
    :raises ValueError: If both track and album are specified.
    """
    if track and album:
        raise ValueError("You must specify either 'track' or 'album', not both.")

    if track:
        target = "track"
        method = "track.getInfo"
        params = {"artist": artist, "track": track}
    elif album:
        target = "album"
        method = "album.getInfo"
        params = {"artist": artist, "album": album}
    else:
        target = "artist"
        method = "artist.getInfo"
        params = {"artist": artist}

    params = params | {
        "method": method,
        "api_key": LASTFM_API_KEY,
        "format": "json",
    }

    r = requests.get(LASTFM_BASE, params=params)
    r.raise_for_status()
    r = r.json()

    if "error" in r and r["error"]:
        raise RuntimeError(
            f"Error during the request for (artist={artist}, track={track}, album={album}). Response:\n{r}"
        )

    data = r[target]
    stats = data.get("stats", {})

    return {
        "name": data.get("name"),
        "listeners": data.get("listeners") or stats.get("listeners"),
        "playcount": data.get("playcount") or stats.get("plays"),
        "meta": {
            "tags": list(
                map(
                    lambda x: x["name"],
                    data.get("toptags", data.get("tags", {})).get("tag", {}),
                )
            ),
            "similar_artist": list(
                map(lambda x: x["name"], data.get("similar", {}).get("artist", {}))
            ),
        },
    }


if __name__ == "__main__":
    mcp.run()
