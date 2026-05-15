"""Collect streaming metrics for a track across Last.fm and SoundCloud.

Usage:
    python -m src.main "Artist Name" "Track Name"

Results are printed as JSON and persisted to the SQLite database via db.save().
"""

import argparse
import json

from data_providers import lastfm, soundcloud
from db import db


def collect(artist: str, track: str) -> dict:
    """Run every relevant provider function for the given (artist, track)."""
    track_query = f"{artist} {track}"
    return {
        "lastfm": {
            "track_listeners": lastfm.get_track_listeners(artist, track),
            "track_playcount": lastfm.get_track_playcount(artist, track),
            "track_tags": lastfm.get_track_tags(artist, track),
            "artist_listeners": lastfm.get_artist_listeners(artist),
            "artist_playcount": lastfm.get_artist_playcount(artist),
            "artist_tags": lastfm.get_artist_tags(artist),
            "artist_similar": lastfm.get_artist_similar(artist),
        },
        "soundcloud": {
            "track_title": soundcloud.get_track_title(track_query),
            "track_artist": soundcloud.get_track_artist(track_query),
            "track_plays": soundcloud.get_track_plays(track_query),
            "track_likes": soundcloud.get_track_likes(track_query),
            "track_reposts": soundcloud.get_track_reposts(track_query),
            "track_comments": soundcloud.get_track_comments(track_query),
            "track_downloads": soundcloud.get_track_downloads(track_query),
            "track_duration": soundcloud.get_track_duration(track_query),
            "track_genre": soundcloud.get_track_genre(track_query),
            "track_created_at": soundcloud.get_track_created_at(track_query),
            "track_tags": soundcloud.get_track_tags(track_query),
            "user_full_name": soundcloud.get_user_full_name(artist),
            "user_followers": soundcloud.get_user_followers(artist),
            "user_following": soundcloud.get_user_following(artist),
            "user_tracks": soundcloud.get_user_tracks(artist),
            "user_playlists": soundcloud.get_user_playlists(artist),
            "user_reposts": soundcloud.get_user_reposts(artist),
            "user_location": soundcloud.get_user_location(artist),
        },
    }


def run() -> None:
    parser = argparse.ArgumentParser(
        description="Collect streaming metrics for a track across Last.fm and SoundCloud."
    )
    parser.add_argument("artist", help="Artist name")
    parser.add_argument("track", help="Track name")
    args = parser.parse_args()

    results = collect(args.artist, args.track)
    db.save(args.artist, args.track, results)

    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    run()
