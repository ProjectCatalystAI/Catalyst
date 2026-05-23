"""
================================================================================
SQLAlchemy Database
================================================================================

This is the structure of the database. It contains the fields retrieved from
the APIs and some columns that will be filled in by the Agent.

Tables:

* catalog
* artist
* spotify_artist
* spotify_artist_historic
* instagram_artist
* instagram_artist_historic
* tiktok_artist
* tiktok_artist_historic
* youtube_artist
* youtube_artist_historic
* track
* spotify_track
* spotify_track_historic
* instagram_track
* instagram_track_historic
* instagram_video_track
* tiktok_track
* tiktok_track_historic
* tiktok_video_track
* youtube_track
* youtube_track_historic
* youtube_video_track
* youtube_short_track
"""

from datetime import date

from sqlalchemy import JSON, Date, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


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
    spotify_id: Mapped[str | None] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)
    bio: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list)
    analysis: Mapped[str | None] = mapped_column(Text)

    tracks: Mapped[list["Track"]] = relationship(back_populates="artist")
    spotify: Mapped["SpotifyArtist | None"] = relationship(back_populates="artist")
    spotify_historic: Mapped[list["SpotifyArtistHistoric"]] = relationship(
        back_populates="artist"
    )
    instagram: Mapped["InstagramArtist | None"] = relationship(back_populates="artist")
    instagram_historic: Mapped[list["InstagramArtistHistoric"]] = relationship(
        back_populates="artist"
    )
    tiktok: Mapped["TiktokArtist | None"] = relationship(back_populates="artist")
    tiktok_historic: Mapped[list["TiktokArtistHistoric"]] = relationship(
        back_populates="artist"
    )
    youtube: Mapped["YoutubeArtist | None"] = relationship(back_populates="artist")
    youtube_historic: Mapped[list["YoutubeArtistHistoric"]] = relationship(
        back_populates="artist"
    )


class SpotifyArtist(Base):
    __tablename__ = "spotify_artist"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    streams: Mapped[int | None] = mapped_column(Integer)
    monthly_listeners: Mapped[int | None] = mapped_column(Integer)
    popularity_current: Mapped[int | None] = mapped_column(Integer)
    followers_total: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="spotify")


class SpotifyArtistHistoric(Base):
    __tablename__ = "spotify_artist_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    date: Mapped[date | None] = mapped_column(Date)
    popularity_current: Mapped[int | None] = mapped_column(Integer)
    followers_total: Mapped[int | None] = mapped_column(Integer)
    monthly_listeners: Mapped[int | None] = mapped_column(Integer)
    streams_total: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="spotify_historic")


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
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="instagram")


class InstagramArtistHistoric(Base):
    __tablename__ = "instagram_artist_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    date: Mapped[date | None] = mapped_column(Date)
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    followers: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="instagram_historic")


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
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="tiktok")


class TiktokArtistHistoric(Base):
    __tablename__ = "tiktok_artist_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    date: Mapped[date | None] = mapped_column(Date)
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    followers: Mapped[int | None] = mapped_column(Integer)
    profile_likes: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="tiktok_historic")


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
    shorts_count: Mapped[int | None] = mapped_column(Integer)
    shorts_views: Mapped[int | None] = mapped_column(Integer)
    shorts_likes: Mapped[int | None] = mapped_column(Integer)
    shorts_comments: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="youtube")


class YoutubeArtistHistoric(Base):
    __tablename__ = "youtube_artist_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    date: Mapped[date | None] = mapped_column(Date)
    subscribers: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    artist: Mapped["Artist"] = relationship(back_populates="youtube_historic")


# ===========================================================================
# Track
# ===========================================================================
class Track(Base):
    __tablename__ = "track"

    id: Mapped[int] = mapped_column(primary_key=True)
    catalog_id: Mapped[int] = mapped_column(ForeignKey("catalog.id"))
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
    spotify_id: Mapped[str | None] = mapped_column(String)
    isrc: Mapped[str | None] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    collaborators: Mapped[str | None] = mapped_column(String)
    release_date: Mapped[date | None] = mapped_column(Date)
    genres: Mapped[list[str]] = mapped_column(JSON, default=list)
    analysis: Mapped[str | None] = mapped_column(Text)
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
    spotify: Mapped["SpotifyTrack | None"] = relationship(back_populates="track")
    spotify_historic: Mapped[list["SpotifyTrackHistoric"]] = relationship(
        back_populates="track"
    )
    instagram: Mapped["InstagramTrack | None"] = relationship(back_populates="track")
    instagram_historic: Mapped[list["InstagramTrackHistoric"]] = relationship(
        back_populates="track"
    )
    tiktok: Mapped["TiktokTrack | None"] = relationship(back_populates="track")
    tiktok_historic: Mapped[list["TiktokTrackHistoric"]] = relationship(
        back_populates="track"
    )
    youtube: Mapped["YoutubeTrack | None"] = relationship(back_populates="track")
    youtube_historic: Mapped[list["YoutubeTrackHistoric"]] = relationship(
        back_populates="track"
    )


class SpotifyTrack(Base):
    __tablename__ = "spotify_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    streams: Mapped[int | None] = mapped_column(Integer)
    popularity: Mapped[int | None] = mapped_column(Integer)
    playlists_current: Mapped[int | None] = mapped_column(Integer)
    playlists_total: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="spotify")


class SpotifyTrackHistoric(Base):
    __tablename__ = "spotify_track_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    date: Mapped[date | None] = mapped_column(Date)
    streams: Mapped[int | None] = mapped_column(Integer)
    popularity: Mapped[int | None] = mapped_column(Integer)
    playlists_current: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="spotify_historic")


class InstagramTrack(Base):
    __tablename__ = "instagram_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    creator_reach: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="instagram")
    videos: Mapped[list["InstagramVideoTrack"]] = relationship(
        back_populates="instagram_track"
    )


class InstagramTrackHistoric(Base):
    __tablename__ = "instagram_track_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    date: Mapped[date | None] = mapped_column(Date)
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="instagram_historic")


class InstagramVideoTrack(Base):
    __tablename__ = "instagram_video_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    instagram_track_id: Mapped[int] = mapped_column(ForeignKey("instagram_track.id"))
    upload_date: Mapped[date | None] = mapped_column(Date)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    video_id: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(String)
    user_country: Mapped[str | None] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String)
    user_followers: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    instagram_track: Mapped["InstagramTrack"] = relationship(back_populates="videos")


class TiktokTrack(Base):
    __tablename__ = "tiktok_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    creator_reach: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="tiktok")
    videos: Mapped[list["TiktokVideoTrack"]] = relationship(
        back_populates="tiktok_track"
    )


class TiktokTrackHistoric(Base):
    __tablename__ = "tiktok_track_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    date: Mapped[date | None] = mapped_column(Date)
    video_count: Mapped[int | None] = mapped_column(Integer)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="tiktok_historic")


class TiktokVideoTrack(Base):
    __tablename__ = "tiktok_video_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    tiktok_track_id: Mapped[int] = mapped_column(ForeignKey("tiktok_track.id"))
    upload_date: Mapped[date | None] = mapped_column(Date)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    shares: Mapped[int | None] = mapped_column(Integer)
    video_id: Mapped[str | None] = mapped_column(String)
    name: Mapped[str | None] = mapped_column(String)
    user_country: Mapped[str | None] = mapped_column(String)
    username: Mapped[str | None] = mapped_column(String)
    user_followers: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    tiktok_track: Mapped["TiktokTrack"] = relationship(back_populates="videos")


class YoutubeTrack(Base):
    __tablename__ = "youtube_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    video_count: Mapped[int | None] = mapped_column(Integer)
    video_views: Mapped[int | None] = mapped_column(Integer)
    video_likes: Mapped[int | None] = mapped_column(Integer)
    video_comments: Mapped[int | None] = mapped_column(Integer)
    shorts_count: Mapped[int | None] = mapped_column(Integer)
    shorts_views: Mapped[int | None] = mapped_column(Integer)
    shorts_likes: Mapped[int | None] = mapped_column(Integer)
    shorts_comments: Mapped[int | None] = mapped_column(Integer)
    creator_reach: Mapped[int | None] = mapped_column(Integer)
    engagement: Mapped[float | None]
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="youtube")
    videos: Mapped[list["YoutubeVideoTrack"]] = relationship(
        back_populates="youtube_track"
    )
    shorts: Mapped[list["YoutubeShortTrack"]] = relationship(
        back_populates="youtube_track"
    )


class YoutubeTrackHistoric(Base):
    __tablename__ = "youtube_track_historic"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("track.id"))
    date: Mapped[date | None] = mapped_column(Date)
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    shorts_count: Mapped[int | None] = mapped_column(Integer)
    analysis: Mapped[str | None] = mapped_column(Text)

    track: Mapped["Track"] = relationship(back_populates="youtube_historic")


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
    external_id: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    upload_date: Mapped[date | None] = mapped_column(Date)
    analysis: Mapped[str | None] = mapped_column(Text)

    youtube_track: Mapped["YoutubeTrack"] = relationship(back_populates="videos")


class YoutubeShortTrack(Base):
    __tablename__ = "youtube_short_track"

    id: Mapped[int] = mapped_column(primary_key=True)
    youtube_track_id: Mapped[int] = mapped_column(ForeignKey("youtube_track.id"))
    views: Mapped[int | None] = mapped_column(Integer)
    likes: Mapped[int | None] = mapped_column(Integer)
    comments: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String)
    external_id: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    upload_date: Mapped[date | None] = mapped_column(Date)
    analysis: Mapped[str | None] = mapped_column(Text)

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
