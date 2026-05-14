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
import re
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

SOUNDCLOUD_BASE = "https://api.soundcloud.com"
SOUNDCLOUD_BASE_V2 = "https://api-v2.soundcloud.com"


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


# ==============================================================================
# Soundcloud Functions
# ==============================================================================
@mcp.tool()
def get_soundcloud_info(query: str, kind: str) -> dict:
    """
    Searches for the best match and returns a cleaned dictionary of relevant fields.

    :param query: The search query string.
    :param kind: The type of resource ('track' or 'user').
    :returns: A dictionary with resource-specific fields:
              - track: 'title', 'artist', 'plays', 'likes', 'reposts', 'comments',
                       'downloads', 'duration_s', 'genre', 'created_at', 'tags'.
              - user: 'full_name', 'followers', 'following', 'tracks',
                      'playlists', 'reposts', 'location'.
    :raises ValueError: If no results are found for the given query.
    """
    data = search_soundcloud(query, kind)

    if kind == "track":
        return {
            "title": data["title"],
            "artist": data["user"]["username"],
            "plays": data.get("playback_count", 0),
            "likes": data.get("likes_count", 0),
            "reposts": data.get("reposts_count", 0),
            "comments": data.get("comment_count", 0),
            "downloads": data.get("download_count", 0),
            "duration_s": data["duration"] // 1000,
            "genre": data.get("genre"),
            "created_at": data.get("created_at"),
            "tags": data.get("tag_list"),
        }
    elif kind == "user":
        return {
            "full_name": data.get("full_name"),
            "followers": data.get("followers_count", 0),
            "following": data.get("followings_count", 0),
            "tracks": data.get("track_count", 0),
            "playlists": data.get("playlist_count", 0),
            "reposts": data.get("reposts_count", 0),
            "location": f"{data.get('city', '')}, {data.get('country_code', '')}".strip(
                ", "
            ),
        }


@mcp.tool()
def search_soundcloud(query: str, kind: str) -> dict:
    """
    Search SoundCloud for a track, artist, or playlist by name.

    :param query: The search query string.
    :param kind: The type of resource to search for ('track' or 'user').
    :returns: A dictionary representing the best matching resource.
    :raises ValueError: If no results are found for the given query.
    """
    client_id = get_soundcloud_client_id()
    r = requests.get(
        f"{SOUNDCLOUD_BASE_V2}/search/{kind}s",
        params={"q": query, "client_id": client_id, "limit": 5},
        headers={"User-Agent": "Mozilla/5.0"},
    )
    r.raise_for_status()
    data = r.json().get("collection", [])
    if not data:
        raise ValueError(f"No results found for {kind.capitalize()}: '{query}'")
    return data[0]  # best match


@mcp.tool()
def get_soundcloud_client_id() -> str:
    """
    Fetches the SoundCloud homepage, finds the JS bundle URLs, and searches
    each bundle for the client_id string.

    :returns: The client_id as a string.
    :raises RuntimeError: If the client_id could not be found in any bundle.
    """
    html = requests.get(
        "https://soundcloud.com", headers={"User-Agent": "Mozilla/5.0"}
    ).text

    js_urls = re.findall(
        r'<script[^>]+src="(https://a-v2\.sndcdn\.com/assets/[^"]+\.js)"', html
    )

    for url in reversed(js_urls):  # last bundles are more likely to have the client_id
        js = requests.get(url).text
        match = re.search(r'client_id\s*:\s*"([a-zA-Z0-9]{32})"', js)
        if match:
            return match.group(1)

    raise RuntimeError("client_id not found")


if __name__ == "__main__":
    mcp.run()
