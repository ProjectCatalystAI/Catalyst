"""
================================================================================
Load Catalogue
================================================================================

File structure:

* load_catalog_from_csv
* get_or_create_artist
* get_or_create_genre
"""

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from db import Artist, Catalog, Database, Genre, Track, TrackGenre


def load_catalog_from_csv(path: str | Path, db: Database) -> Catalog:
    """
    Load a CSV file and persist its contents as a new catalog in the database.
    Each row in the CSV represents a track. The catalog name is derived from the file name.
    :param path: Path to the CSV file. Expected columns: title, artist, collaborators, genres, release_date.
    :param db: The Database instance to use for the session.
    :returns: The newly created Catalog instance.
    :raises FileNotFoundError: If the CSV file does not exist at the given path.
    """
    path = Path(path)

    with db.session() as session:
        catalog = Catalog(name=path.stem)
        session.add(catalog)
        session.flush()

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                artist = get_or_create_artist(session, row["artist"].strip())

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

        session.commit()
        return catalog


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
