"""
================================================================================
SQLAlchemy Database
================================================================================

This is the structure of the database. It contains the field retrieved from
the APIs and some columns that will be fill in by the Agent.

Tables:

* genre
* track_genre
* catalog
* artist
* instagram_artist
* tiktok_artist
* youtube_artist
* track
* instagram_track
* instagram_video_track
* tiktok_track
* tiktok_video_track
* youtube_track
* youtube_video_track
* youtube_short_track
"""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ===========================================================================
# Genre
# ===========================================================================
class Genre(Base):
    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)

    tracks: Mapped[list["TrackGenre"]] = relationship(back_populates="genre")


class TrackGenre(Base):
    __tablename__ = "track_genre"

    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"), primary_key=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.id"), primary_key=True)

    track: Mapped["Track"] = relationship(back_populates="genres")
    genre: Mapped["Genre"] = relationship(back_populates="tracks")


# ===========================================================================
# Catalog
# ===========================================================================
class Catalog(Base):
    __tablename__ = "catalog"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)

    tracks: Mapped[list["Track"]] = relationship(back_populates="catalog")


# ===========================================================================
# Artist
# ===========================================================================
class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    summary: Mapped[str | None] = mapped_column(Text)
    instagram_analysis: Mapped[str | None] = mapped_column(Text)
    tiktok_analysis: Mapped[str | None] = mapped_column(Text)
    youtube_analysis: Mapped[str | None] = mapped_column(Text)

    tracks: Mapped[list["Track"]] = relationship(back_populates="artist")
    instagram: Mapped["InstagramArtist | None"] = relationship(back_populates="artist")
    tiktok: Mapped["TiktokArtist | None"] = relationship(back_populates="artist")
    youtube: Mapped["YoutubeArtist | None"] = relationship(back_populates="artist")


class InstagramArtist(Base):
    __tablename__ = "instagram_artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    followers: Mapped[int | None] = mapped_column(Integer)
    video_reach: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]

    artist: Mapped["Artist"] = relationship(back_populates="instagram")


class TiktokArtist(Base):
    __tablename__ = "tiktok_artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    followers: Mapped[int | None] = mapped_column(Integer)
    profile_likes: Mapped[int | None] = mapped_column(Integer)
    video_reach: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]

    artist: Mapped["Artist"] = relationship(back_populates="tiktok")


class YoutubeArtist(Base):
    __tablename__ = "youtube_artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    creator_reach: Mapped[int | None] = mapped_column(Integer)
    subscribers: Mapped[int | None] = mapped_column(Integer)
    channel_views: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]
    video_count: Mapped[int | None] = mapped_column(Integer)
    video_views: Mapped[int | None] = mapped_column(Integer)
    video_likes: Mapped[int | None] = mapped_column(Integer)
    video_comments: Mapped[int | None] = mapped_column(Integer)
    video_reach: Mapped[int | None] = mapped_column(Integer)
    short_count: Mapped[int | None] = mapped_column(Integer)
    shorts_views: Mapped[int | None] = mapped_column(Integer)
    shorts_likes: Mapped[int | None] = mapped_column(Integer)
    shorts_comments: Mapped[int | None] = mapped_column(Integer)

    artist: Mapped["Artist"] = relationship(back_populates="youtube")


# ===========================================================================
# Track
# ===========================================================================
class Track(Base):
    __tablename__ = "track"

    id: Mapped[int] = mapped_column(primary_key=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalog.id"))
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    title: Mapped[str] = mapped_column(String)
    collaborators: Mapped[str | None] = mapped_column(String)
    release_date: Mapped[date | None] = mapped_column(Date)
    summary: Mapped[str | None] = mapped_column(Text)
    instagram_analysis: Mapped[str | None] = mapped_column(Text)
    instagram_top5_videos_analysis: Mapped[str | None] = mapped_column(Text)
    tiktok_analysis: Mapped[str | None] = mapped_column(Text)
    tiktok_top5_videos_analysis: Mapped[str | None] = mapped_column(Text)
    youtube_analysis: Mapped[str | None] = mapped_column(Text)
    youtube_top5_videos_analysis: Mapped[str | None] = mapped_column(Text)
    youtube_top5_shorts_analysis: Mapped[str | None] = mapped_column(Text)

    catalog: Mapped["Catalog"] = relationship(back_populates="tracks")
    artist: Mapped["Artist"] = relationship(back_populates="tracks")
    genres: Mapped[list["TrackGenre"]] = relationship(back_populates="track")
    instagram: Mapped["InstagramTrack | None"] = relationship(back_populates="track")
    tiktok: Mapped["TiktokTrack | None"] = relationship(back_populates="track")
    youtube: Mapped["YoutubeTrack | None"] = relationship(back_populates="track")


class InstagramTrack(Base):
    __tablename__ = "instagram_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    creator_reach: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]

    track: Mapped["Track"] = relationship(back_populates="instagram")
    videos: Mapped[list["InstagramVideoTrack"]] = relationship(
        back_populates="instagram_track"
    )


class InstagramVideoTrack(Base):
    __tablename__ = "instagram_video_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_track_id: Mapped[int] = mapped_column(ForeignKey("instagram_track.id"))
    upload_date: Mapped[date | None] = mapped_column(Date)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str | None] = mapped_column(String)
    name: Mapped[str | None] = mapped_column(String)
    user_country: Mapped[str | None] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String)
    user_followers: Mapped[int | None] = mapped_column(Integer)

    instagram_track: Mapped["InstagramTrack"] = relationship(back_populates="videos")


class TiktokTrack(Base):
    __tablename__ = "tiktok_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    creator_reach: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]

    track: Mapped["Track"] = relationship(back_populates="tiktok")
    videos: Mapped[list["TiktokVideoTrack"]] = relationship(
        back_populates="tiktok_track"
    )


class TiktokVideoTrack(Base):
    __tablename__ = "tiktok_video_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    tiktok_track_id: Mapped[int] = mapped_column(ForeignKey("tiktok_track.id"))
    upload_date: Mapped[date | None] = mapped_column(Date)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str | None] = mapped_column(String)
    name: Mapped[str | None] = mapped_column(String)
    user_country: Mapped[str | None] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String)
    user_followers: Mapped[int | None] = mapped_column(Integer)

    tiktok_track: Mapped["TiktokTrack"] = relationship(back_populates="videos")


class YoutubeTrack(Base):
    __tablename__ = "youtube_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)

    track: Mapped["Track"] = relationship(back_populates="youtube")
    videos: Mapped[list["YoutubeVideoTrack"]] = relationship(
        back_populates="youtube_track"
    )
    shorts: Mapped[list["YoutubeShortTrack"]] = relationship(
        back_populates="youtube_track"
    )


class YoutubeVideoTrack(Base):
    __tablename__ = "youtube_video_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    youtube_track_id: Mapped[int] = mapped_column(ForeignKey("youtube_track.id"))
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    dislikes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    record_date: Mapped[date | None] = mapped_column(Date)
    title: Mapped[str | None] = mapped_column(String)
    image_url: Mapped[str | None] = mapped_column(String)
    upload_date: Mapped[date | None] = mapped_column(Date)

    youtube_track: Mapped["YoutubeTrack"] = relationship(back_populates="videos")


class YoutubeShortTrack(Base):
    __tablename__ = "youtube_short_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    youtube_track_id: Mapped[int] = mapped_column(ForeignKey("youtube_track.id"))
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String)
    upload_date: Mapped[date | None] = mapped_column(Date)

    youtube_track: Mapped["YoutubeTrack"] = relationship(back_populates="shorts")


# ===========================================================================
# Database
# ===========================================================================
class Database:
    def __init__(self, url: str = "sqlite:///catalyst.db"):
        self.engine = create_engine(url)
        Base.metadata.create_all(self.engine)

    def session(self) -> Session:
        return Session(self.engine)


if __name__ == "__main__":
    db = Database()
    print("Database created successfully.")
