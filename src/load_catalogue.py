"""
================================================================================
Load Catalogue
================================================================================

File structure:

* load_catalog_from_csv
* get_or_create_artist
* get_or_create_genre
* populate_artist
    Fetch and persist bio, country, and all platform stats for an artist.
    Resolves the Spotify ID if not set. Each platform is attempted
    independently; failures are logged and silently skipped.
* populate_track
    Fetch and persist Spotify ID, ISRC, and all platform stats for a track.
    Each platform is attempted independently; failures are logged and skipped.
* _spotify_artist_id (private)
    Search Spotify for an artist by name and return their ID.
* _spotify_track_ids (private)
    Search Spotify for a track by title+artist and return (track_id, artist_id).
"""

import csv
import logging
import requests
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy.orm import Session

from db import (
    Artist,
    Catalog,
    Database,
    Genre,
    InstagramArtist,
    InstagramArtistHistoric,
    InstagramTrack,
    InstagramTrackHistoric,
    InstagramVideoTrack,
    SpotifyArtist,
    SpotifyArtistHistoric,
    SpotifyTrack,
    SpotifyTrackHistoric,
    TiktokArtist,
    TiktokArtistHistoric,
    TiktokTrack,
    TiktokTrackHistoric,
    TiktokVideoTrack,
    Track,
    TrackGenre,
    YoutubeArtist,
    YoutubeArtistHistoric,
    YoutubeShortTrack,
    YoutubeTrack,
    YoutubeTrackHistoric,
    YoutubeVideoTrack,
)
from utils import parse_date
from streaming_analyst import (
    token as _spotify_token,
    get_artist_bio_and_country,
    get_instagram_artist_historic,
    get_instagram_artist_stats,
    get_instagram_track_historic,
    get_instagram_track_stats,
    get_spotify_artist_historic,
    get_spotify_artist_stats,
    get_spotify_track_stats,
    get_tiktok_artist_historic,
    get_tiktok_artist_stats,
    get_tiktok_track_historic,
    get_tiktok_track_stats,
    get_track_daily_streams,
    get_track_genres,
    get_track_isrc,
    get_youtube_artist_historic,
    get_youtube_artist_stats,
    get_youtube_track_historic,
    get_youtube_track_stats,
)

log = logging.getLogger(__name__)


# ==============================================================================
# CSV Loading
# ==============================================================================
def load_catalog_from_csv(
    path: str | Path,
    db: Database,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Catalog:
    """
    Load a CSV file and persist its contents as a new catalog in the database,
    including all available platform stats for each artist and track.

    :param path: Path to the CSV file. Expected columns: title, artist,
                 collaborators, genres, release_date.
    :param db: The Database instance to use for the session.
    :param start_date: Start of the historic window (YYYY-MM-DD). Defaults to
                       two years ago.
    :param end_date: End of the historic window (YYYY-MM-DD). Defaults to
                     today.
    :returns: The newly created Catalog instance.
    :raises FileNotFoundError: If the CSV file does not exist at the given
                               path.
    """
    path = Path(path)

    today = date.today()
    if end_date is None:
        end_date = (today - timedelta(days=1)).isoformat()
    if start_date is None:
        start_date = date(today.year - 1, 1, 1).isoformat()

    with db.session() as session:
        catalog = Catalog(name=path.stem)
        session.add(catalog)
        session.flush()

        populated_artists: set[int] = set()

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                artist = get_or_create_artist(session, row["artist"].strip())

                if artist.id not in populated_artists:
                    populate_artist(session, artist, start_date, end_date)
                    populated_artists.add(artist.id)

                track = Track(
                    catalog_id=catalog.id,
                    artist_id=artist.id,
                    title=row["title"].strip(),
                    collaborators=row.get("collaborators", "").strip() or None,
                    release_date=parse_date(row.get("release_date", "")),
                )
                session.add(track)
                session.flush()

                raw_genres = row.get("genres", "")
                for genre_name in raw_genres.split(","):
                    genre_name = genre_name.strip()
                    if genre_name:
                        genre = get_or_create_genre(session, genre_name)
                        session.add(TrackGenre(track_id=track.id, genre_id=genre.id))

                track_start = (
                    track.release_date.isoformat() if track.release_date else start_date
                )
                populate_track(session, track, artist, track_start, end_date)

        session.commit()
        session.refresh(catalog)
        return catalog


# ==============================================================================
# Artist Helpers
# ==============================================================================
def get_or_create_artist(session: Session, name: str) -> Artist:
    """
    Retrieve an existing artist by name or create a new one if not found.

    :param session: The active SQLAlchemy session.
    :param name: The artist name to look up or create.
    :returns: The existing or newly created Artist instance.
    """
    artist = session.query(Artist).filter_by(name=name).first()
    if not artist:
        artist = Artist(name=name)
        session.add(artist)
        session.flush()
    return artist


def get_or_create_genre(session: Session, name: str) -> Genre:
    """
    Retrieve an existing genre by name or create a new one if not found.

    :param session: The active SQLAlchemy session.
    :param name: The genre name to look up or create.
    :returns: The existing or newly created Genre instance.
    """
    genre = session.query(Genre).filter_by(name=name).first()
    if not genre:
        genre = Genre(name=name)
        session.add(genre)
        session.flush()
    return genre


# ==============================================================================
# Date Parsing Helper
# ==============================================================================
_DATE_FIELDS = {"date", "upload_date", "record_date"}


def _parse_dates(entry: dict) -> dict:
    """Convert any string value whose key is a known date field to a date object."""
    return {
        k: parse_date(v) if k in _DATE_FIELDS and isinstance(v, str) else v
        for k, v in entry.items()
    }


# ==============================================================================
# Artist Population
# ==============================================================================
def populate_artist(
    session: Session, artist: Artist, start_date: str, end_date: str
) -> None:
    """
    Fetch and persist bio, country, and all platform stats for an artist.

    Resolves the Spotify ID if not already set. Each platform is wrapped in a
    savepoint so that a failure on one does not taint the session for the
    others. Does nothing if the Spotify ID cannot be resolved.

    :param session: The active SQLAlchemy session.
    :param artist: Artist instance already flushed to the session.
    :param start_date: Start of the historic window (YYYY-MM-DD).
    :param end_date: End of the historic window (YYYY-MM-DD).
    """
    if not artist.spotify_id:
        artist.spotify_id = _spotify_artist_id(artist.name)
        session.flush()
    if not artist.spotify_id:
        log.warning("No Spotify ID for '%s'; skipping artist population.", artist.name)
        return

    sid = artist.spotify_id
    name = artist.name  # capture before any potential expiry

    try:
        with session.begin_nested():
            info = get_artist_bio_and_country(name)
            artist.bio = info.get("bio")
            artist.country = info.get("country")
    except Exception as e:
        log.warning("Bio/country failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            session.add(SpotifyArtist(artist_id=artist.id, **get_spotify_artist_stats(sid)))
    except Exception as e:
        log.warning("Spotify artist stats failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            for entry in get_spotify_artist_historic(sid, start_date, end_date):
                session.add(SpotifyArtistHistoric(artist_id=artist.id, **_parse_dates(entry)))
    except Exception as e:
        log.warning("Spotify artist historic failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            session.add(InstagramArtist(artist_id=artist.id, **get_instagram_artist_stats(sid)))
    except Exception as e:
        log.warning("Instagram artist stats failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            for entry in get_instagram_artist_historic(sid, start_date, end_date):
                session.add(InstagramArtistHistoric(artist_id=artist.id, **_parse_dates(entry)))
    except Exception as e:
        log.warning("Instagram artist historic failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            session.add(TiktokArtist(artist_id=artist.id, **get_tiktok_artist_stats(sid)))
    except Exception as e:
        log.warning("TikTok artist stats failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            for entry in get_tiktok_artist_historic(sid, start_date, end_date):
                session.add(TiktokArtistHistoric(artist_id=artist.id, **_parse_dates(entry)))
    except Exception as e:
        log.warning("TikTok artist historic failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            session.add(YoutubeArtist(artist_id=artist.id, **get_youtube_artist_stats(sid)))
    except Exception as e:
        log.warning("YouTube artist stats failed for '%s': %s", name, e)

    try:
        with session.begin_nested():
            for entry in get_youtube_artist_historic(sid, start_date, end_date):
                session.add(YoutubeArtistHistoric(artist_id=artist.id, **_parse_dates(entry)))
    except Exception as e:
        log.warning("YouTube artist historic failed for '%s': %s", name, e)


# ==============================================================================
# Track Population
# ==============================================================================
def populate_track(
    session: Session, track: Track, artist: Artist, start_date: str, end_date: str
) -> None:
    """
    Fetch and persist Spotify ID, ISRC, and all platform stats for a track.

    Each platform is attempted independently so that a failure on one does not
    block the others. Skips platform population if the ISRC or artist Spotify
    ID cannot be resolved.

    :param session: The active SQLAlchemy session.
    :param track: Track instance already flushed to the session.
    :param artist: The track's artist (needed for platform lookups).
    :param start_date: Start of the historic window (YYYY-MM-DD).
    :param end_date: End of the historic window (YYYY-MM-DD).
    """
    if not track.spotify_id:
        ids = _spotify_track_ids(track.title, artist.name)
        if ids:
            track.spotify_id, spotify_artist_id = ids
            if not artist.spotify_id:
                artist.spotify_id = spotify_artist_id
            session.flush()

    if not track.isrc and track.spotify_id:
        try:
            track.isrc = get_track_isrc(track.spotify_id)
            session.flush()
        except Exception as e:
            log.warning("ISRC lookup failed for '%s': %s", track.title, e)

    if not track.isrc or not track.spotify_id or not artist.spotify_id:
        log.warning(
            "Missing ISRC, Spotify track ID, or artist Spotify ID for '%s'; skipping platform population.",
            track.title,
        )
        return

    isrc = track.isrc
    track_sid = track.spotify_id
    artist_sid = artist.spotify_id
    title = track.title  # capture before any potential expiry

    try:
        with session.begin_nested():
            existing_genre_ids = {tg.genre_id for tg in session.query(TrackGenre).filter_by(track_id=track.id)}
            for name in get_track_genres(isrc, track_sid):
                genre = get_or_create_genre(session, name)
                if genre.id not in existing_genre_ids:
                    session.add(TrackGenre(track_id=track.id, genre_id=genre.id))
                    existing_genre_ids.add(genre.id)
    except Exception as e:
        log.warning("Track genres failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            session.add(SpotifyTrack(track_id=track.id, **get_spotify_track_stats(isrc, track_sid, artist_sid)))
    except Exception as e:
        log.warning("Spotify track stats failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            for entry in get_track_daily_streams(track_sid, artist_sid, start_date, end_date):
                session.add(SpotifyTrackHistoric(
                    track_id=track.id,
                    date=parse_date(entry["date"]),
                    streams=entry.get("streams_daily"),
                    popularity=None,
                    playlists_current=None,
                ))
    except Exception as e:
        log.warning("Spotify track historic failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            stats = get_instagram_track_stats(isrc, track_sid, artist_sid)
            videos = stats.pop("videos", [])
            ig_track = InstagramTrack(track_id=track.id, **stats)
            session.add(ig_track)
            session.flush()
            for v in videos:
                session.add(InstagramVideoTrack(instagram_track_id=ig_track.id, **_parse_dates(v)))
    except Exception as e:
        log.warning("Instagram track stats failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            for entry in get_instagram_track_historic(isrc, track_sid, artist_sid, start_date, end_date):
                session.add(InstagramTrackHistoric(track_id=track.id, **_parse_dates(entry)))
    except Exception as e:
        log.warning("Instagram track historic failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            stats = get_tiktok_track_stats(isrc, track_sid, artist_sid)
            videos = stats.pop("videos", [])
            tt_track = TiktokTrack(track_id=track.id, **stats)
            session.add(tt_track)
            session.flush()
            for v in videos:
                session.add(TiktokVideoTrack(tiktok_track_id=tt_track.id, **_parse_dates(v)))
    except Exception as e:
        log.warning("TikTok track stats failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            for entry in get_tiktok_track_historic(isrc, track_sid, artist_sid, start_date, end_date):
                session.add(TiktokTrackHistoric(track_id=track.id, **_parse_dates(entry)))
    except Exception as e:
        log.warning("TikTok track historic failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            stats = get_youtube_track_stats(isrc, track_sid, artist_sid)
            videos = stats.pop("videos", [])
            shorts = stats.pop("shorts", [])
            yt_track = YoutubeTrack(track_id=track.id, **stats)
            session.add(yt_track)
            session.flush()
            for v in videos:
                session.add(YoutubeVideoTrack(youtube_track_id=yt_track.id, **_parse_dates(v)))
            for s in shorts:
                session.add(YoutubeShortTrack(youtube_track_id=yt_track.id, **_parse_dates(s)))
    except Exception as e:
        log.warning("YouTube track stats failed for '%s': %s", title, e)

    try:
        with session.begin_nested():
            for entry in get_youtube_track_historic(isrc, track_sid, artist_sid, start_date, end_date):
                session.add(YoutubeTrackHistoric(track_id=track.id, **_parse_dates(entry)))
    except Exception as e:
        log.warning("YouTube track historic failed for '%s': %s", title, e)


# ==============================================================================
# Spotify ID Helpers (private)
# ==============================================================================
def _spotify_artist_id(name: str) -> str | None:
    """
    Search Spotify for an artist by name and return their ID.

    :param name: Artist name to search for.
    :returns: Spotify artist ID string, or None if not found or on error.
    """
    try:
        r = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {_spotify_token.get()}"},
            params={"q": name, "type": "artist", "limit": 1},
            timeout=15,
        )
        r.raise_for_status()
        items = r.json().get("artists", {}).get("items", [])
        return items[0]["id"] if items else None
    except Exception as e:
        log.warning("Spotify artist ID lookup failed for '%s': %s", name, e)
        return None


def _spotify_track_ids(title: str, artist: str) -> tuple[str, str] | None:
    """
    Search Spotify for a track by title and artist name and return IDs.

    :param title: Track title.
    :param artist: Artist name.
    :returns: (track_id, artist_id) tuple, or None if not found or on error.
    """
    try:
        r = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {_spotify_token.get()}"},
            params={
                "q": f"track:{title} artist:{artist}",
                "type": "track",
                "limit": 1,
            },
            timeout=15,
        )
        r.raise_for_status()
        items = r.json().get("tracks", {}).get("items", [])
        if not items:
            return None
        return items[0]["id"], items[0]["artists"][0]["id"]
    except Exception as e:
        log.warning("Spotify track ID lookup failed for '%s' by '%s': %s", title, artist, e)
        return None
