import requests

from config import LASTFM_API_KEY, LASTFM_BASE


def _fetch(target: str, params: dict) -> dict:
    """Call Last.fm getInfo for the given target and return the inner data dict."""
    params = params | {
        "method": f"{target}.getInfo",
        "api_key": LASTFM_API_KEY,
        "format": "json",
    }
    r = requests.get(LASTFM_BASE, params=params)
    r.raise_for_status()
    r = r.json()

    if "error" in r and r["error"]:
        raise RuntimeError(f"Last.fm error for params={params}. Response:\n{r}")

    return r[target]


def _artist(artist: str) -> dict:
    return _fetch("artist", {"artist": artist})


def _track(artist: str, track: str) -> dict:
    return _fetch("track", {"artist": artist, "track": track})


def _album(artist: str, album: str) -> dict:
    return _fetch("album", {"artist": artist, "album": album})


def _listeners(data: dict) -> str:
    return data.get("listeners") or data.get("stats", {}).get("listeners")


def _playcount(data: dict) -> str:
    return data.get("playcount") or data.get("stats", {}).get("plays")


def _tags(data: dict) -> list[str]:
    container = data.get("toptags", data.get("tags", {}))
    return [t["name"] for t in container.get("tag", [])]


def _similar_artists(data: dict) -> list[str]:
    return [a["name"] for a in data.get("similar", {}).get("artist", [])]


# ==============================================================================
# Artist
# ==============================================================================
def get_artist_listeners(artist: str) -> str:
    """Number of Last.fm listeners for an artist."""
    return _listeners(_artist(artist))


def get_artist_playcount(artist: str) -> str:
    """Total Last.fm playcount for an artist."""
    return _playcount(_artist(artist))


def get_artist_tags(artist: str) -> list[str]:
    """Top user-applied tags for an artist."""
    return _tags(_artist(artist))


def get_artist_similar(artist: str) -> list[str]:
    """Names of artists Last.fm considers similar."""
    return _similar_artists(_artist(artist))


# ==============================================================================
# Track
# ==============================================================================
def get_track_listeners(artist: str, track: str) -> str:
    """Number of Last.fm listeners for a track."""
    return _listeners(_track(artist, track))


def get_track_playcount(artist: str, track: str) -> str:
    """Total Last.fm playcount for a track."""
    return _playcount(_track(artist, track))


def get_track_tags(artist: str, track: str) -> list[str]:
    """Top user-applied tags for a track."""
    return _tags(_track(artist, track))


# ==============================================================================
# Album
# ==============================================================================
def get_album_listeners(artist: str, album: str) -> str:
    """Number of Last.fm listeners for an album."""
    return _listeners(_album(artist, album))


def get_album_playcount(artist: str, album: str) -> str:
    """Total Last.fm playcount for an album."""
    return _playcount(_album(artist, album))


def get_album_tags(artist: str, album: str) -> list[str]:
    """Top user-applied tags for an album."""
    return _tags(_album(artist, album))
