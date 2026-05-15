import re

import requests

from config import SOUNDCLOUD_BASE_V2


def _get_client_id() -> str:
    """
    Fetches the SoundCloud homepage, finds the JS bundle URLs, and searches
    each bundle for the client_id string.
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


def _search(query: str, kind: str) -> dict:
    """Search SoundCloud for the best match of the given kind."""
    client_id = _get_client_id()
    r = requests.get(
        f"{SOUNDCLOUD_BASE_V2}/search/{kind}s",
        params={"q": query, "client_id": client_id, "limit": 5},
        headers={"User-Agent": "Mozilla/5.0"},
    )
    r.raise_for_status()
    data = r.json().get("collection", [])
    if not data:
        raise ValueError(f"No results found for {kind.capitalize()}: '{query}'")
    return data[0]


def _track(query: str) -> dict:
    return _search(query, "track")


def _user(query: str) -> dict:
    return _search(query, "user")


# ==============================================================================
# Track
# ==============================================================================
def get_track_title(query: str) -> str:
    """Title of the best-matching track."""
    return _track(query)["title"]


def get_track_artist(query: str) -> str:
    """Uploader username of the best-matching track."""
    return _track(query)["user"]["username"]


def get_track_plays(query: str) -> int:
    """Playback count of the best-matching track."""
    return _track(query).get("playback_count", 0)


def get_track_likes(query: str) -> int:
    """Like count of the best-matching track."""
    return _track(query).get("likes_count", 0)


def get_track_reposts(query: str) -> int:
    """Repost count of the best-matching track."""
    return _track(query).get("reposts_count", 0)


def get_track_comments(query: str) -> int:
    """Comment count of the best-matching track."""
    return _track(query).get("comment_count", 0)


def get_track_downloads(query: str) -> int:
    """Download count of the best-matching track."""
    return _track(query).get("download_count", 0)


def get_track_duration(query: str) -> int:
    """Duration of the best-matching track, in seconds."""
    return _track(query)["duration"] // 1000


def get_track_genre(query: str) -> str | None:
    """Genre tag of the best-matching track."""
    return _track(query).get("genre")


def get_track_created_at(query: str) -> str | None:
    """ISO creation timestamp of the best-matching track."""
    return _track(query).get("created_at")


def get_track_tags(query: str) -> str | None:
    """Raw tag_list string of the best-matching track."""
    return _track(query).get("tag_list")


# ==============================================================================
# User
# ==============================================================================
def get_user_full_name(query: str) -> str | None:
    """Display name of the best-matching user."""
    return _user(query).get("full_name")


def get_user_followers(query: str) -> int:
    """Follower count of the best-matching user."""
    return _user(query).get("followers_count", 0)


def get_user_following(query: str) -> int:
    """Number of users the best-matching user follows."""
    return _user(query).get("followings_count", 0)


def get_user_tracks(query: str) -> int:
    """Number of tracks uploaded by the best-matching user."""
    return _user(query).get("track_count", 0)


def get_user_playlists(query: str) -> int:
    """Number of playlists owned by the best-matching user."""
    return _user(query).get("playlist_count", 0)


def get_user_reposts(query: str) -> int:
    """Number of reposts by the best-matching user."""
    return _user(query).get("reposts_count", 0)


def get_user_location(query: str) -> str:
    """'City, CountryCode' for the best-matching user (may be empty)."""
    data = _user(query)
    return f"{data.get('city', '')}, {data.get('country_code', '')}".strip(", ")
