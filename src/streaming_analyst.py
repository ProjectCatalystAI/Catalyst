import os
import time

import requests
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]


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
            auth=(CLIENT_ID, CLIENT_SECRET),
        )
        r.raise_for_status()
        return r.json()["access_token"]


mcp = FastMCP("spotify-charts")
token = AccessToken()


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

    if r.status_code != 200:
        raise RuntimeError(f"Spotify API error {r.status_code}: {r.text}")

    return r.json()["popularity"]


if __name__ == "__main__":
    mcp.run()
