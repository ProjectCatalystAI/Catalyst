import json
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    fetched_at: Mapped[datetime]

    lastfm_listeners: Mapped[str | None]
    lastfm_playcount: Mapped[str | None]
    lastfm_tags: Mapped[str | None]
    lastfm_similar: Mapped[str | None]

    soundcloud_full_name: Mapped[str | None]
    soundcloud_followers: Mapped[int | None]
    soundcloud_following: Mapped[int | None]
    soundcloud_tracks: Mapped[int | None]
    soundcloud_playlists: Mapped[int | None]
    soundcloud_reposts: Mapped[int | None]
    soundcloud_location: Mapped[str | None]


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist: Mapped[str]
    name: Mapped[str]
    fetched_at: Mapped[datetime]

    lastfm_listeners: Mapped[str | None]
    lastfm_playcount: Mapped[str | None]
    lastfm_tags: Mapped[str | None]

    soundcloud_title: Mapped[str | None]
    soundcloud_artist: Mapped[str | None]
    soundcloud_plays: Mapped[int | None]
    soundcloud_likes: Mapped[int | None]
    soundcloud_reposts: Mapped[int | None]
    soundcloud_comments: Mapped[int | None]
    soundcloud_downloads: Mapped[int | None]
    soundcloud_duration: Mapped[int | None]
    soundcloud_genre: Mapped[str | None]
    soundcloud_created_at: Mapped[str | None]
    soundcloud_tags: Mapped[str | None]


class Database:
    def __init__(self, url: str = "sqlite:///catalyst.db"):
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)

    @staticmethod
    def _json(value) -> str | None:
        return json.dumps(value) if value is not None else None

    def save(self, artist: str, track: str, results: dict) -> None:
        """Persist one Artist row and one Track row from a collect() result dict."""
        now = datetime.now(timezone.utc)
        lastfm = results.get("lastfm", {})
        soundcloud = results.get("soundcloud", {})

        artist_row = Artist(
            name=artist,
            fetched_at=now,
            lastfm_listeners=lastfm.get("artist_listeners"),
            lastfm_playcount=lastfm.get("artist_playcount"),
            lastfm_tags=self._json(lastfm.get("artist_tags")),
            lastfm_similar=self._json(lastfm.get("artist_similar")),
            soundcloud_full_name=soundcloud.get("user_full_name"),
            soundcloud_followers=soundcloud.get("user_followers"),
            soundcloud_following=soundcloud.get("user_following"),
            soundcloud_tracks=soundcloud.get("user_tracks"),
            soundcloud_playlists=soundcloud.get("user_playlists"),
            soundcloud_reposts=soundcloud.get("user_reposts"),
            soundcloud_location=soundcloud.get("user_location"),
        )

        track_row = Track(
            artist=artist,
            name=track,
            fetched_at=now,
            lastfm_listeners=lastfm.get("track_listeners"),
            lastfm_playcount=lastfm.get("track_playcount"),
            lastfm_tags=self._json(lastfm.get("track_tags")),
            soundcloud_title=soundcloud.get("track_title"),
            soundcloud_artist=soundcloud.get("track_artist"),
            soundcloud_plays=soundcloud.get("track_plays"),
            soundcloud_likes=soundcloud.get("track_likes"),
            soundcloud_reposts=soundcloud.get("track_reposts"),
            soundcloud_comments=soundcloud.get("track_comments"),
            soundcloud_downloads=soundcloud.get("track_downloads"),
            soundcloud_duration=soundcloud.get("track_duration"),
            soundcloud_genre=soundcloud.get("track_genre"),
            soundcloud_created_at=soundcloud.get("track_created_at"),
            soundcloud_tags=soundcloud.get("track_tags"),
        )

        with Session(self.engine) as session:
            session.add(artist_row)
            session.add(track_row)
            session.commit()


db = Database()
