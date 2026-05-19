"""
================================================================================
Streaming Analyst
================================================================================

The following functions can be run by agents using MCP to retrieve information
about artists, tracks, and albums on various DSPs.

File structure:

* Songstats helpers (private)
    * _songstats_get
        Base GET wrapper that injects auth headers and the base URL.
    * _songstats_source_data
        Calls _songstats_get and extracts the data dict for a given source from
        the stats envelope.

* Spotify functions
    * get_spotify_track_stats
        Return current Spotify stats for a track: streams, popularity,
        playlists_current, playlists_total.
    * get_track_daily_streams
        Return Daily streams and Total streams of a track in the range
        start_date - end_date. This could be use for both history loading and
        daily update of the history (using the date of yesterday as both
        start_date and end_date).
    * get_spotify_artist_stats
        Return current Spotify stats for an artist: monthly_listeners,
        followers_total, streams, popularity_current.
    * get_spotify_artist_historic
        Return a list of historic daily snapshots for an artist on Spotify.
    * get_popularity
        Return the popularity index. Useful to estimate the recent raising of
        popularity of an artist, track, or album.
    * search_spotify_id
        Auxiliary function for the previous one that searches for a query.

* Instagram functions
    * get_instagram_artist_stats
        Return current Instagram stats for an artist.
    * get_instagram_artist_historic
        Return historic Instagram snapshots for an artist.
    * get_instagram_track_stats
        Return current Instagram stats for a track, including top videos.
    * get_instagram_track_historic
        Return historic Instagram snapshots for a track.

* TikTok functions
    * get_tiktok_artist_stats
        Return current TikTok stats for an artist.
    * get_tiktok_artist_historic
        Return historic TikTok snapshots for an artist.
    * get_tiktok_track_stats
        Return current TikTok stats for a track, including top videos.
    * get_tiktok_track_historic
        Return historic TikTok snapshots for a track.

* YouTube functions
    * get_youtube_artist_stats
        Return current YouTube stats for an artist.
    * get_youtube_artist_historic
        Return historic YouTube snapshots for an artist.
    * get_youtube_track_stats
        Return current YouTube stats for a track, including top videos and
        top shorts.
    * get_youtube_track_historic
        Return historic YouTube snapshots for a track.

* Track metadata functions
    * get_track_isrc
        Return the ISRC of a track using the Spotify API.

* MusicBrainz functions
    * get_artist_bio_and_country
        Return the country of origin and a Wikipedia biography excerpt for an
        artist, sourced from MusicBrainz and the Wikipedia REST API.

* Last.FM functions
    * get_lastfm_info
        Return various information such as playcount, listeners, genres, and
        similar artists.

* Soundcloud functions
    * get_soundcloud_info
        Return various information about tracks and users. Soundcloud has no
        native album type; they are treated as playlists.
    * search_soundcloud
        Auxiliary function for the previous one that searches for a query.
    * get_soundcloud_client_id
        We need to send a get request to the Soundcloud webpage in order to get
        the Client ID. This has to be done for every call to search_soundcloud,
        adding an overhead of a couple of seconds. Since these functions are
        called by an agent, it's not a big deal, and there are not other viable
        alternatives as far as I know.

TODO: If we want to monitor specific artists, tracks, or albums, we could let
      the agent execute these functions periodically (e.g., once a day) to save
      the relevant data into a CSV. It would help to understand how much an
      artist, track, or album is raising (e.g., monitoring the popularity
      index).
TODO: Functions that accept queries such as search_spotify_id and
      search_soundcloud return the first element of the search. While this will
      be correct most of the times, a more precise implementation should return
      a list of multiple elements (e.g., 5) among which the agent will choose
      the most relevant one.
TODO: At the end, we could cross-reference all the gathered data.
"""

import os
import re
import time
from datetime import date
from typing import Any

import requests
from dotenv import load_dotenv

from server import mcp

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

SONGSTATS_API_KEY = os.environ["SONGSTATS_API_KEY"]
SONGSTATS_BASE = "https://api.songstats.com/enterprise/v1"


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


token = AccessToken()


# ==============================================================================
# Spotify Functions
# ==============================================================================
def get_spotify_track_stats(
    isrc: str, spotify_track_id: str, spotify_artist_id: str
) -> dict:
    """
    Get current Spotify stats for a track from Songstats.

    :param isrc: ISRC code of the track
    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API
                              keys)
    :returns: dict with keys 'streams', 'popularity', 'playlists_current',
              'playlists_total'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "tracks/stats",
        {
            "isrc": isrc,
            "spotify_track_id": spotify_track_id,
            "spotify_artist_id": spotify_artist_id,
            "offset": 0,
        },
        "spotify",
    )
    return {
        "streams": data.get("streams_total"),
        "popularity": data.get("popularity_current"),
        "playlists_current": data.get("playlists_editorial_current"),
        "playlists_total": data.get("playlists_editorial_total"),
    }


def get_track_daily_streams(
    spotify_track_id: str,
    spotify_artist_id: str,
    start_date: str,
    end_date: str,
    source: str = "spotify",
) -> list[dict]:
    """
    Get daily stream counts for a track from Songstats.

    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API keys)
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :param source: platform to query (default: 'spotify')
    :returns: list of dicts with keys 'date', 'streams_daily', 'streams_total'
    :raises requests.HTTPError: if the API call fails
    """
    params: dict = {
        "source": source,
        "start_date": start_date,
        "end_date": end_date,
        "spotify_track_id": spotify_track_id,
        "spotify_artist_id": spotify_artist_id,
    }

    resp = requests.get(
        f"{SONGSTATS_BASE}/tracks/historic_stats",
        headers={"apikey": SONGSTATS_API_KEY, "Accept": "application/json"},
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    history = data["stats"][0]["data"]["history"]

    return [
        {
            "date": entry["date"],
            "streams_daily": entry.get("streams_daily"),
            "streams_total": entry.get("streams_total"),
        }
        for entry in history
    ]


# ==============================================================================
# Songstats Helpers
# ==============================================================================
def _songstats_get(endpoint: str, params: dict) -> dict:
    """
    Base GET wrapper for the Songstats Enterprise API.

    :param endpoint: path relative to SONGSTATS_BASE (e.g. 'artists/stats')
    :param params: query parameters to include in the request
    :returns: parsed JSON response
    :raises requests.HTTPError: if the API call fails
    """
    resp = requests.get(
        f"{SONGSTATS_BASE}/{endpoint}",
        headers={"apikey": SONGSTATS_API_KEY, "Accept": "application/json"},
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def _songstats_source_data(endpoint: str, params: dict, source: str) -> dict:
    """
    Call Songstats and extract the data dict for a specific source from the
    stats envelope.

    :param endpoint: path relative to SONGSTATS_BASE
    :param params: query parameters (without 'source', which is injected here)
    :param source: platform name (e.g. 'spotify', 'instagram', 'tiktok',
                   'youtube')
    :returns: the 'data' dict for the matching source entry, or {} if not found
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_get(endpoint, {**params, "source": source})
    for entry in data.get("stats", []):
        if entry.get("source") == source:
            return entry.get("data", {})
    return {}


def _songstats_track_stats_paginated(
    params: dict, source: str, *video_keys: str
) -> tuple[dict, dict[str, list]]:
    """
    Fetch tracks/stats with video pagination for a given source.

    Starts at offset=0 and increments by 100 until no new items are found in
    any of the requested video_keys.

    :param params: base query params (isrc, spotify_track_id, spotify_artist_id)
    :param source: platform name ('youtube', 'tiktok', 'instagram')
    :param video_keys: keys inside 'data' that hold video lists (e.g. 'videos',
                       'shorts')
    :returns: (aggregate_data_dict, {key: [all_items]})
    :raises requests.HTTPError: if any API call fails
    """
    base = {**params, "source": source, "with_videos": "true", "limit": 100}

    def _extract(resp: dict) -> dict:
        for entry in resp.get("stats", []):
            if entry.get("source") == source:
                return entry.get("data", {})
        return {}

    first_data = _extract(_songstats_get("tracks/stats", {**base, "offset": 0}))
    all_items: dict[str, list] = {k: list(first_data.get(k, [])) for k in video_keys}

    offset = 100
    while True:
        page_data = _extract(_songstats_get("tracks/stats", {**base, "offset": offset}))
        found = False
        for k in video_keys:
            page = page_data.get(k, [])
            if page:
                all_items[k].extend(page)
                found = True
        if not found:
            break
        offset += 100

    return first_data, all_items


# ==============================================================================
# Spotify Artist Functions
# ==============================================================================
def get_spotify_artist_stats(spotify_artist_id: str) -> dict:
    """
    Get current Spotify stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :returns: dict with keys 'monthly_listeners', 'followers_total', 'streams',
              'popularity_current'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/stats",
        {"spotify_artist_id": spotify_artist_id},
        "spotify",
    )
    return {
        "monthly_listeners": data.get("monthly_listeners_current"),
        "followers_total": data.get("followers_total"),
        "streams": data.get("streams_total"),
        "popularity_current": data.get("popularity_current"),
    }


def get_spotify_artist_historic(
    spotify_artist_id: str, start_date: str, end_date: str
) -> list[dict]:
    """
    Get historic Spotify stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :returns: list of dicts with keys 'date', 'popularity_current',
              'followers_total', 'monthly_listeners', 'streams_total'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/historic_stats",
        {
            "spotify_artist_id": spotify_artist_id,
            "start_date": start_date,
            "end_date": end_date,
            "with_aggregates": "true",
        },
        "spotify",
    )
    return [
        {
            "date": entry.get("date"),
            "popularity_current": entry.get("popularity_current"),
            "followers_total": entry.get("followers_total"),
            "monthly_listeners": entry.get("monthly_listeners_current"),
            "streams_total": entry.get("streams_total"),
        }
        for entry in data.get("history", [])
    ]


@mcp.tool()
def get_popularity(query: str, kind: str) -> int:
    """
    Get Spotify popularity score (0-100) for a track, artist, or album.

    :param query: search string (e.g. 'Purple Rain')
    :param kind: one of 'track', 'artist', 'album'
    :raises ValueError: if kind is invalid
    :raises RuntimeError: if the API call fails
    """
    if kind not in ("track", "artist", "album"):
        raise ValueError(
            f"Invalid kind '{kind}'. Must be 'track', 'artist', or 'album'."
        )

    spotify_id = search_spotify_id(query, kind)
    access_token = token.get()

    url = f"https://api.spotify.com/v1/{kind}s/{spotify_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    return r.json()["popularity"]


def search_spotify_id(query: str, kind: str) -> tuple[str]:
    """
    Search for a track/artist/album by name and return its Spotify ID.

    :param query: search string (e.g. 'Purple Rain')
    :param kind: one of 'track', 'artist', 'album'
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

    return (items[0]["id"], items[0]["artists"][0]["id"])


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


# ==============================================================================
# Instagram Artist Functions
# ==============================================================================
def get_instagram_artist_stats(spotify_artist_id: str) -> dict:
    """
    Get current Instagram stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :returns: dict with keys 'video_count', 'views', 'likes', 'comments',
              'followers', 'video_reach', 'engagement'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/stats",
        {"spotify_artist_id": spotify_artist_id},
        "instagram",
    )
    return {
        "video_count": data.get("videos_total"),
        "views": data.get("views_total"),
        "likes": data.get("likes_total"),
        "comments": data.get("comments_total"),
        "followers": data.get("followers_total"),
        "video_reach": data.get("video_reach_total"),
        "engagement": data.get("engagement_rate_total"),
    }


def get_instagram_artist_historic(
    spotify_artist_id: str, start_date: str, end_date: str
) -> list[dict]:
    """
    Get historic Instagram stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :returns: list of dicts with keys 'date', 'video_count', 'views', 'likes',
              'comments', 'followers'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/historic_stats",
        {
            "spotify_artist_id": spotify_artist_id,
            "start_date": start_date,
            "end_date": end_date,
            "with_aggregates": "true",
        },
        "instagram",
    )
    return [
        {
            "date": entry.get("date"),
            "video_count": entry.get("videos_total"),
            "views": entry.get("views_total"),
            "likes": entry.get("likes_total"),
            "comments": entry.get("comments_total"),
            "followers": entry.get("followers_total"),
        }
        for entry in data.get("history", [])
    ]


# ==============================================================================
# Instagram Track Functions
# ==============================================================================
def get_instagram_track_stats(
    isrc: str, spotify_track_id: str, spotify_artist_id: str
) -> dict:
    """
    Get current Instagram stats for a track from Songstats, including all
    videos (paginated in batches of 100).

    :param isrc: ISRC code of the track
    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API
                              keys)
    :returns: dict with keys 'video_count', 'views', 'likes', 'comments',
              'creator_reach', 'engagement', and 'videos' (list of dicts with
              'upload_date', 'views', 'likes', 'comments', 'video_id',
              'user_country', 'username', 'user_handle', 'user_followers')
    :raises requests.HTTPError: if the API call fails
    """
    data, items = _songstats_track_stats_paginated(
        {"isrc": isrc, "spotify_track_id": spotify_track_id, "spotify_artist_id": spotify_artist_id},
        "instagram",
        "videos",
    )
    videos = [
        {
            "upload_date": v.get("upload_date"),
            "views": v.get("views_total"),
            "likes": v.get("likes_total"),
            "comments": v.get("comments_total"),
            "video_id": v.get("instagram_video_id"),
            "user_country": v.get("instagram_user_country"),
            "username": v.get("instagram_user_handle"),
            "user_followers": v.get("instagram_user_followers"),
        }
        for v in items["videos"]
    ]
    return {
        "video_count": data.get("videos_total"),
        "views": data.get("views_total"),
        "likes": data.get("likes_total"),
        "comments": data.get("comments_total"),
        "creator_reach": data.get("creator_reach_total"),
        "engagement": data.get("engagement_rate_total"),
        "videos": videos,
    }


def get_instagram_track_historic(
    isrc: str, spotify_track_id: str, spotify_artist_id: str, start_date: str, end_date: str
) -> list[dict]:
    """
    Get historic Instagram stats for a track from Songstats.

    :param isrc: ISRC code of the track
    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API
                              keys)
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :returns: list of dicts with keys 'date', 'video_count', 'views', 'likes',
              'comments'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "tracks/historic_stats",
        {
            "isrc": isrc,
            "spotify_track_id": spotify_track_id,
            "spotify_artist_id": spotify_artist_id,
            "start_date": start_date,
            "end_date": end_date,
        },
        "instagram",
    )
    return [
        {
            "date": entry.get("date"),
            "video_count": entry.get("videos_total"),
            "views": entry.get("views_total"),
            "likes": entry.get("likes_total"),
            "comments": entry.get("comments_total"),
        }
        for entry in data.get("history", [])
    ]


# ==============================================================================
# TikTok Artist Functions
# ==============================================================================
def get_tiktok_artist_stats(spotify_artist_id: str) -> dict:
    """
    Get current TikTok stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :returns: dict with keys 'video_count', 'views', 'likes', 'shares',
              'comments', 'followers', 'profile_likes', 'video_reach',
              'engagement'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/stats",
        {"spotify_artist_id": spotify_artist_id},
        "tiktok",
    )
    return {
        "video_count": data.get("videos_total"),
        "views": data.get("views_total"),
        "likes": data.get("likes_total"),
        "shares": data.get("shares_total"),
        "comments": data.get("comments_total"),
        "followers": data.get("followers_total"),
        "profile_likes": data.get("profile_likes_total"),
        "video_reach": data.get("video_reach_total"),
        "engagement": data.get("engagement_rate_total"),
    }


def get_tiktok_artist_historic(
    spotify_artist_id: str, start_date: str, end_date: str
) -> list[dict]:
    """
    Get historic TikTok stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :returns: list of dicts with keys 'date', 'video_count', 'views', 'likes',
              'shares', 'comments', 'followers', 'profile_likes'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/historic_stats",
        {
            "spotify_artist_id": spotify_artist_id,
            "start_date": start_date,
            "end_date": end_date,
            "with_aggregates": "true",
        },
        "tiktok",
    )
    return [
        {
            "date": entry.get("date"),
            "video_count": entry.get("videos_total"),
            "views": entry.get("views_total"),
            "likes": entry.get("likes_total"),
            "shares": entry.get("shares_total"),
            "comments": entry.get("comments_total"),
            "followers": entry.get("followers_total"),
            "profile_likes": entry.get("profile_likes_total"),
        }
        for entry in data.get("history", [])
    ]


# ==============================================================================
# TikTok Track Functions
# ==============================================================================
def get_tiktok_track_stats(
    isrc: str, spotify_track_id: str, spotify_artist_id: str
) -> dict:
    """
    Get current TikTok stats for a track from Songstats, including all videos
    (paginated in batches of 100).

    :param isrc: ISRC code of the track
    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API
                              keys)
    :returns: dict with keys 'video_count', 'views', 'likes', 'shares',
              'comments', 'creator_reach', 'engagement', and 'videos' (list of
              dicts with 'upload_date', 'views', 'likes', 'comments', 'shares',
              'video_id', 'user_country', 'username', 'user_handle',
              'user_followers')
    :raises requests.HTTPError: if the API call fails
    """
    data, items = _songstats_track_stats_paginated(
        {"isrc": isrc, "spotify_track_id": spotify_track_id, "spotify_artist_id": spotify_artist_id},
        "tiktok",
        "videos",
    )
    videos = [
        {
            "upload_date": v.get("upload_date"),
            "views": v.get("views_total"),
            "likes": v.get("likes_total"),
            "comments": v.get("comments_total"),
            "shares": v.get("shares_total"),
            "video_id": v.get("tiktok_video_id"),
            "user_country": v.get("tiktok_user_country"),
            "username": v.get("tiktok_user_handle"),
            "user_followers": v.get("tiktok_user_followers"),
        }
        for v in items["videos"]
    ]
    return {
        "video_count": data.get("videos_total"),
        "views": data.get("views_total"),
        "likes": data.get("likes_total"),
        "shares": data.get("shares_total"),
        "comments": data.get("comments_total"),
        "creator_reach": data.get("creator_reach_total"),
        "engagement": data.get("engagement_rate_total"),
        "videos": videos,
    }


def get_tiktok_track_historic(
    isrc: str, spotify_track_id: str, spotify_artist_id: str, start_date: str, end_date: str
) -> list[dict]:
    """
    Get historic TikTok stats for a track from Songstats.

    :param isrc: ISRC code of the track
    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API
                              keys)
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :returns: list of dicts with keys 'date', 'video_count', 'views', 'likes',
              'shares', 'comments'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "tracks/historic_stats",
        {
            "isrc": isrc,
            "spotify_track_id": spotify_track_id,
            "spotify_artist_id": spotify_artist_id,
            "start_date": start_date,
            "end_date": end_date,
        },
        "tiktok",
    )
    return [
        {
            "date": entry.get("date"),
            "video_count": entry.get("videos_total"),
            "views": entry.get("views_total"),
            "likes": entry.get("likes_total"),
            "shares": entry.get("shares_total"),
            "comments": entry.get("comments_total"),
        }
        for entry in data.get("history", [])
    ]


# ==============================================================================
# YouTube Artist Functions
# ==============================================================================
def get_youtube_artist_stats(spotify_artist_id: str) -> dict:
    """
    Get current YouTube stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :returns: dict with keys 'subscribers', 'channel_views', 'engagement',
              'video_count', 'video_views', 'video_likes', 'video_comments',
              'video_reach', 'shorts_count', 'shorts_views', 'shorts_likes',
              'shorts_comments'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/stats",
        {"spotify_artist_id": spotify_artist_id},
        "youtube",
    )
    return {
        "subscribers": data.get("subscribers_total"),
        "channel_views": data.get("channel_views_total"),
        "engagement": data.get("engagement_rate_total"),
        "video_count": data.get("videos_total"),
        "video_views": data.get("video_views_total"),
        "video_likes": data.get("video_likes_total"),
        "video_comments": data.get("video_comments_total"),
        "video_reach": data.get("video_reach_total"),
        "shorts_count": data.get("shorts_total"),
        "shorts_views": data.get("short_views_total"),
        "shorts_likes": data.get("short_likes_total"),
        "shorts_comments": data.get("short_comments_total"),
    }


def get_youtube_artist_historic(
    spotify_artist_id: str, start_date: str, end_date: str
) -> list[dict]:
    """
    Get historic YouTube stats for an artist from Songstats.

    :param spotify_artist_id: Spotify artist ID
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :returns: list of dicts with keys 'date', 'subscribers', 'views', 'likes',
              'comments'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "artists/historic_stats",
        {
            "spotify_artist_id": spotify_artist_id,
            "start_date": start_date,
            "end_date": end_date,
            "with_aggregates": "true",
        },
        "youtube",
    )
    return [
        {
            "date": entry.get("date"),
            "subscribers": entry.get("subscribers_total"),
            "views": entry.get("video_views_total"),
            "likes": entry.get("video_likes_total"),
            "comments": entry.get("video_comments_total"),
        }
        for entry in data.get("history", [])
    ]


# ==============================================================================
# YouTube Track Functions
# ==============================================================================
def get_youtube_track_stats(
    isrc: str, spotify_track_id: str, spotify_artist_id: str
) -> dict:
    """
    Get current YouTube stats for a track from Songstats, including all videos
    and shorts (paginated in batches of 100).

    :param isrc: ISRC code of the track
    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API
                              keys)
    :returns: dict with keys 'video_count', 'video_views', 'video_likes',
              'video_comments', 'shorts_count', 'shorts_views', 'shorts_likes',
              'shorts_comments', 'creator_reach', 'engagement', 'videos' (list
              of dicts with 'views', 'likes', 'dislikes', 'comments',
              'record_date', 'title', 'external_id', 'upload_date'), and
              'shorts' (list of dicts with 'views', 'likes', 'comments',
              'title', 'external_id', 'upload_date')
    :raises requests.HTTPError: if the API call fails
    """
    data, items = _songstats_track_stats_paginated(
        {"isrc": isrc, "spotify_track_id": spotify_track_id, "spotify_artist_id": spotify_artist_id},
        "youtube",
        "videos",
        "shorts",
    )
    videos = [
        {
            "views": v.get("view_count"),
            "likes": v.get("like_count"),
            "dislikes": v.get("dislike_count"),
            "comments": v.get("comment_count"),
            "record_date": v.get("record_date"),
            "title": v.get("title"),
            "external_id": v.get("external_id"),
            "upload_date": v.get("upload_date"),
        }
        for v in items["videos"]
    ]
    shorts = [
        {
            "views": s.get("view_count"),
            "likes": s.get("like_count"),
            "comments": s.get("comment_count"),
            "title": s.get("title"),
            "external_id": s.get("external_id"),
            "upload_date": s.get("upload_date"),
        }
        for s in items["shorts"]
    ]
    return {
        "video_count": data.get("videos_total"),
        "video_views": data.get("video_views_total"),
        "video_likes": data.get("video_likes_total"),
        "video_comments": data.get("video_comments_total"),
        "shorts_count": data.get("shorts_total"),
        "shorts_views": data.get("short_views_total"),
        "shorts_likes": data.get("short_likes_total"),
        "shorts_comments": data.get("short_comments_total"),
        "creator_reach": data.get("creator_reach_total"),
        "engagement": data.get("engagement_rate_total"),
        "videos": videos,
        "shorts": shorts,
    }


def get_youtube_track_historic(
    isrc: str, spotify_track_id: str, spotify_artist_id: str, start_date: str, end_date: str
) -> list[dict]:
    """
    Get historic YouTube stats for a track from Songstats.

    :param isrc: ISRC code of the track
    :param spotify_track_id: Spotify track ID
    :param spotify_artist_id: Spotify artist ID (required for Artist/Label API
                              keys)
    :param start_date: start of the time window (YYYY-MM-DD)
    :param end_date: end of the time window (YYYY-MM-DD)
    :returns: list of dicts with keys 'date', 'views', 'likes', 'comments',
              'shorts_count'
    :raises requests.HTTPError: if the API call fails
    """
    data = _songstats_source_data(
        "tracks/historic_stats",
        {
            "isrc": isrc,
            "spotify_track_id": spotify_track_id,
            "spotify_artist_id": spotify_artist_id,
            "start_date": start_date,
            "end_date": end_date,
        },
        "youtube",
    )
    return [
        {
            "date": entry.get("date"),
            "views": entry.get("video_views_total"),
            "likes": entry.get("video_likes_total"),
            "comments": entry.get("video_comments_total"),
            "shorts_count": entry.get("shorts_total"),
        }
        for entry in data.get("history", [])
    ]


# ==============================================================================
# Track Metadata Functions
# ==============================================================================
def get_track_isrc(spotify_track_id: str) -> str | None:
    """
    Get the ISRC of a track from the Spotify API.

    :param spotify_track_id: Spotify track ID
    :returns: ISRC string (e.g. 'USRC17607839'), or None if not available
    :raises requests.HTTPError: if the API call fails
    """
    access_token = token.get()
    r = requests.get(
        f"https://api.spotify.com/v1/tracks/{spotify_track_id}",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("external_ids", {}).get("isrc")


# ==============================================================================
# MusicBrainz Functions
# ==============================================================================
_MUSICBRAINZ_BASE = "https://musicbrainz.org/ws/2"
_MUSICBRAINZ_UA = "Catalyst/1.0 (alessiocelentano2003@gmail.com)"


def get_artist_bio_and_country(artist_name: str) -> dict:
    """
    Fetch the country of origin and a short biography for an artist.

    Uses MusicBrainz to look up the artist and obtain their country and MBID,
    then follows the Wikipedia URL relation (if present) to fetch a biography
    excerpt from the Wikipedia REST summary API.

    :param artist_name: artist name to search for
    :returns: dict with keys 'country' (ISO 3166-1 alpha-2 code or None) and
              'bio' (plain-text Wikipedia extract or None)
    :raises requests.HTTPError: if any API call fails
    """
    r = requests.get(
        f"{_MUSICBRAINZ_BASE}/artist/",
        params={"query": f"artist:{artist_name}", "fmt": "json", "limit": 1},
        headers={"User-Agent": _MUSICBRAINZ_UA},
        timeout=15,
    )
    r.raise_for_status()
    artists = r.json().get("artists", [])
    if not artists:
        return {"country": None, "bio": None}

    artist = artists[0]
    country = artist.get("country")
    mbid = artist.get("id")

    time.sleep(1)
    r = requests.get(
        f"{_MUSICBRAINZ_BASE}/artist/{mbid}",
        params={"inc": "url-rels", "fmt": "json"},
        headers={"User-Agent": _MUSICBRAINZ_UA},
        timeout=15,
    )
    r.raise_for_status()

    bio = None
    for rel in r.json().get("relations", []):
        if rel.get("type") in ("wikipedia", "wikidata"):
            url = rel.get("url", {}).get("resource", "")
            title = url.rstrip("/").split("/")[-1]
            time.sleep(0.5)
            wiki_r = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}",
                timeout=15,
            )
            if wiki_r.ok:
                bio = wiki_r.json().get("extract")
            break

    return {"country": country, "bio": bio}
