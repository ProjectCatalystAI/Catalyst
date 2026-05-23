"""SQLAlchemy fetch tools.

One tool per platform/table. Each tool accepts `track_id: int` and returns a
JSON-serialisable dict (or list of dicts). Video tools include a fully built
URL so the agent does not need to construct one.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import desc, nulls_last
from strands import tool

from src.db import (
    Artist,
    Database,
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
    YoutubeArtist,
    YoutubeArtistHistoric,
    YoutubeShortTrack,
    YoutubeTrack,
    YoutubeTrackHistoric,
    YoutubeVideoTrack,
)

_db = Database()


def _iso(d: Any) -> str | None:
    return d.isoformat() if d is not None else None


# ---------------------------------------------------------------------------
# Spotify
# ---------------------------------------------------------------------------
@tool
def fetch_spotify_track_stats(track_id: int) -> dict:
    """Fetch current Spotify metrics (streams, popularity, playlists) for a track."""
    with _db.session() as s:
        row = s.query(SpotifyTrack).filter_by(track_id=track_id).one_or_none()
        if row is None:
            return {"error": f"no spotify_track row for track_id={track_id}"}
        return {
            "streams": row.streams,
            "popularity": row.popularity,
            "playlists_current": row.playlists_current,
            "playlists_total": row.playlists_total,
        }


@tool
def fetch_spotify_track_historic(track_id: int) -> list[dict]:
    """Fetch the chronological Spotify history for a track (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(SpotifyTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(SpotifyTrackHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "streams": r.streams,
                "popularity": r.popularity,
                "playlists_current": r.playlists_current,
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------
@tool
def fetch_instagram_track_stats(track_id: int) -> dict:
    """Fetch current Instagram aggregate metrics for a track."""
    with _db.session() as s:
        row = s.query(InstagramTrack).filter_by(track_id=track_id).one_or_none()
        if row is None:
            return {"error": f"no instagram_track row for track_id={track_id}"}
        return {
            "video_count": row.video_count,
            "views": row.views,
            "likes": row.likes,
            "comments": row.comments,
            "creator_reach": row.creator_reach,
            "engagement": row.engagement,
        }


@tool
def fetch_instagram_track_historic(track_id: int) -> list[dict]:
    """Fetch the chronological Instagram aggregate history (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(InstagramTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(InstagramTrackHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "video_count": r.video_count,
                "views": r.views,
                "likes": r.likes,
                "comments": r.comments,
            }
            for r in rows
        ]


@tool
def fetch_top5_instagram_videos(track_id: int) -> list[dict]:
    """Top 5 Instagram videos for a track by views (descending). URL included."""
    with _db.session() as s:
        ig = s.query(InstagramTrack).filter_by(track_id=track_id).one_or_none()
        if ig is None:
            return []
        rows = (
            s.query(InstagramVideoTrack)
            .filter_by(instagram_track_id=ig.id)
            .order_by(nulls_last(desc(InstagramVideoTrack.views)))
            .limit(5)
            .all()
        )
        out = []
        for r in rows:
            if not r.video_id:
                continue
            out.append(
                {
                    "id": r.id,
                    "video_id": r.video_id,
                    "url": f"https://www.instagram.com/reels/{r.video_id}",
                    "views": r.views,
                    "likes": r.likes,
                    "comments": r.comments,
                    "username": r.username,
                }
            )
        return out


# ---------------------------------------------------------------------------
# TikTok
# ---------------------------------------------------------------------------
@tool
def fetch_tiktok_track_stats(track_id: int) -> dict:
    """Fetch current TikTok aggregate metrics for a track."""
    with _db.session() as s:
        row = s.query(TiktokTrack).filter_by(track_id=track_id).one_or_none()
        if row is None:
            return {"error": f"no tiktok_track row for track_id={track_id}"}
        return {
            "video_count": row.video_count,
            "views": row.views,
            "likes": row.likes,
            "shares": row.shares,
            "comments": row.comments,
            "creator_reach": row.creator_reach,
            "engagement": row.engagement,
        }


@tool
def fetch_tiktok_track_historic(track_id: int) -> list[dict]:
    """Fetch the chronological TikTok aggregate history (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(TiktokTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(TiktokTrackHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "video_count": r.video_count,
                "views": r.views,
                "likes": r.likes,
                "shares": r.shares,
                "comments": r.comments,
            }
            for r in rows
        ]


@tool
def fetch_top5_tiktok_videos(track_id: int) -> list[dict]:
    """Top 5 TikTok videos for a track by views (descending). URL included.

    URL format requires the creator handle, which is stored as `username`.
    Videos without both username and video_id are skipped.
    """
    with _db.session() as s:
        tt = s.query(TiktokTrack).filter_by(track_id=track_id).one_or_none()
        if tt is None:
            return []
        rows = (
            s.query(TiktokVideoTrack)
            .filter_by(tiktok_track_id=tt.id)
            .order_by(nulls_last(desc(TiktokVideoTrack.views)))
            .limit(5)
            .all()
        )
        out = []
        for r in rows:
            if not r.video_id or not r.username:
                continue
            out.append(
                {
                    "id": r.id,
                    "video_id": r.video_id,
                    "url": f"https://www.tiktok.com/@{r.username}/video/{r.video_id}",
                    "views": r.views,
                    "likes": r.likes,
                    "shares": r.shares,
                    "comments": r.comments,
                    "username": r.username,
                }
            )
        return out


# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------
@tool
def fetch_youtube_track_stats(track_id: int) -> dict:
    """Fetch current YouTube aggregate metrics (video + shorts) for a track."""
    with _db.session() as s:
        row = s.query(YoutubeTrack).filter_by(track_id=track_id).one_or_none()
        if row is None:
            return {"error": f"no youtube_track row for track_id={track_id}"}
        return {
            "video_count": row.video_count,
            "video_views": row.video_views,
            "video_likes": row.video_likes,
            "video_comments": row.video_comments,
            "shorts_count": row.shorts_count,
            "shorts_views": row.shorts_views,
            "shorts_likes": row.shorts_likes,
            "shorts_comments": row.shorts_comments,
            "creator_reach": row.creator_reach,
            "engagement": row.engagement,
        }


@tool
def fetch_youtube_track_historic(track_id: int) -> list[dict]:
    """Fetch the chronological YouTube aggregate history (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(YoutubeTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(YoutubeTrackHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "views": r.views,
                "likes": r.likes,
                "comments": r.comments,
                "shorts_count": r.shorts_count,
            }
            for r in rows
        ]


@tool
def fetch_top5_youtube_videos(track_id: int) -> list[dict]:
    """Top 5 YouTube long-form videos for a track by views (descending)."""
    with _db.session() as s:
        yt = s.query(YoutubeTrack).filter_by(track_id=track_id).one_or_none()
        if yt is None:
            return []
        rows = (
            s.query(YoutubeVideoTrack)
            .filter_by(youtube_track_id=yt.id)
            .order_by(nulls_last(desc(YoutubeVideoTrack.views)))
            .limit(5)
            .all()
        )
        out = []
        for r in rows:
            if not r.external_id:
                continue
            out.append(
                {
                    "id": r.id,
                    "external_id": r.external_id,
                    "url": f"https://www.youtube.com/watch?v={r.external_id}",
                    "title": r.title,
                    "views": r.views,
                    "likes": r.likes,
                    "comments": r.comments,
                }
            )
        return out


@tool
def fetch_top5_youtube_shorts(track_id: int) -> list[dict]:
    """Top 5 YouTube Shorts for a track by views (descending)."""
    with _db.session() as s:
        yt = s.query(YoutubeTrack).filter_by(track_id=track_id).one_or_none()
        if yt is None:
            return []
        rows = (
            s.query(YoutubeShortTrack)
            .filter_by(youtube_track_id=yt.id)
            .order_by(nulls_last(desc(YoutubeShortTrack.views)))
            .limit(5)
            .all()
        )
        out = []
        for r in rows:
            if not r.external_id:
                continue
            out.append(
                {
                    "id": r.id,
                    "external_id": r.external_id,
                    "url": f"https://www.youtube.com/shorts/{r.external_id}",
                    "title": r.title,
                    "views": r.views,
                    "likes": r.likes,
                    "comments": r.comments,
                }
            )
        return out


# ---------------------------------------------------------------------------
# Per-source summary helpers — one per platform
# ---------------------------------------------------------------------------
@tool
def fetch_spotify_analyses(track_id: int) -> dict:
    """Fetch every Spotify analysis stored for a track (current + historic)."""
    with _db.session() as s:
        track = s.query(Track).filter_by(id=track_id).one_or_none()
        if track is None:
            return {"error": f"no track row for track_id={track_id}"}
        spotify = s.query(SpotifyTrack).filter_by(track_id=track_id).one_or_none()
        spotify_hist = (
            s.query(SpotifyTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(SpotifyTrackHistoric.date.desc())
            .first()
        )
        return {
            "title": track.title,
            "current": spotify.analysis if spotify else None,
            "historic": spotify_hist.analysis if spotify_hist else None,
        }


@tool
def fetch_instagram_analyses(track_id: int) -> dict:
    """Fetch every Instagram analysis stored for a track (current + historic + videos)."""
    with _db.session() as s:
        track = s.query(Track).filter_by(id=track_id).one_or_none()
        if track is None:
            return {"error": f"no track row for track_id={track_id}"}
        instagram = s.query(InstagramTrack).filter_by(track_id=track_id).one_or_none()
        instagram_hist = (
            s.query(InstagramTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(InstagramTrackHistoric.date.desc())
            .first()
        )
        videos = []
        if instagram is not None:
            videos = [v.analysis for v in instagram.videos if v.analysis]
        return {
            "title": track.title,
            "current": instagram.analysis if instagram else None,
            "historic": instagram_hist.analysis if instagram_hist else None,
            "top_videos": videos,
        }


@tool
def fetch_tiktok_analyses(track_id: int) -> dict:
    """Fetch every TikTok analysis stored for a track (current + historic + videos)."""
    with _db.session() as s:
        track = s.query(Track).filter_by(id=track_id).one_or_none()
        if track is None:
            return {"error": f"no track row for track_id={track_id}"}
        tiktok = s.query(TiktokTrack).filter_by(track_id=track_id).one_or_none()
        tiktok_hist = (
            s.query(TiktokTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(TiktokTrackHistoric.date.desc())
            .first()
        )
        videos = []
        if tiktok is not None:
            videos = [v.analysis for v in tiktok.videos if v.analysis]
        return {
            "title": track.title,
            "current": tiktok.analysis if tiktok else None,
            "historic": tiktok_hist.analysis if tiktok_hist else None,
            "top_videos": videos,
        }


@tool
def fetch_youtube_analyses(track_id: int) -> dict:
    """Fetch every YouTube analysis stored for a track (current + historic + videos + shorts)."""
    with _db.session() as s:
        track = s.query(Track).filter_by(id=track_id).one_or_none()
        if track is None:
            return {"error": f"no track row for track_id={track_id}"}
        youtube = s.query(YoutubeTrack).filter_by(track_id=track_id).one_or_none()
        youtube_hist = (
            s.query(YoutubeTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(YoutubeTrackHistoric.date.desc())
            .first()
        )
        videos = []
        shorts = []
        if youtube is not None:
            videos = [v.analysis for v in youtube.videos if v.analysis]
            shorts = [v.analysis for v in youtube.shorts if v.analysis]
        return {
            "title": track.title,
            "current": youtube.analysis if youtube else None,
            "historic": youtube_hist.analysis if youtube_hist else None,
            "top_videos": videos,
            "top_shorts": shorts,
        }


# ---------------------------------------------------------------------------
# Summary helper — used by the Track Summarizer
# ---------------------------------------------------------------------------
@tool
def fetch_all_analyses(track_id: int) -> dict:
    """Fetch every per-platform analysis already stored for a track."""
    with _db.session() as s:
        track = s.query(Track).filter_by(id=track_id).one_or_none()
        if track is None:
            return {"error": f"no track row for track_id={track_id}"}

        spotify = s.query(SpotifyTrack).filter_by(track_id=track_id).one_or_none()
        spotify_hist = (
            s.query(SpotifyTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(SpotifyTrackHistoric.date.desc())
            .first()
        )
        instagram = s.query(InstagramTrack).filter_by(track_id=track_id).one_or_none()
        instagram_hist = (
            s.query(InstagramTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(InstagramTrackHistoric.date.desc())
            .first()
        )
        tiktok = s.query(TiktokTrack).filter_by(track_id=track_id).one_or_none()
        tiktok_hist = (
            s.query(TiktokTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(TiktokTrackHistoric.date.desc())
            .first()
        )
        youtube = s.query(YoutubeTrack).filter_by(track_id=track_id).one_or_none()
        youtube_hist = (
            s.query(YoutubeTrackHistoric)
            .filter_by(track_id=track_id)
            .order_by(YoutubeTrackHistoric.date.desc())
            .first()
        )

        instagram_videos = []
        if instagram is not None:
            instagram_videos = [
                v.analysis
                for v in instagram.videos
                if v.analysis
            ]
        tiktok_videos = []
        if tiktok is not None:
            tiktok_videos = [v.analysis for v in tiktok.videos if v.analysis]
        youtube_videos = []
        youtube_shorts = []
        if youtube is not None:
            youtube_videos = [v.analysis for v in youtube.videos if v.analysis]
            youtube_shorts = [v.analysis for v in youtube.shorts if v.analysis]

        return {
            "title": track.title,
            "spotify": spotify.analysis if spotify else None,
            "spotify_historic": spotify_hist.analysis if spotify_hist else None,
            "instagram": instagram.analysis if instagram else None,
            "instagram_historic": instagram_hist.analysis if instagram_hist else None,
            "instagram_top_videos": instagram_videos,
            "tiktok": tiktok.analysis if tiktok else None,
            "tiktok_historic": tiktok_hist.analysis if tiktok_hist else None,
            "tiktok_top_videos": tiktok_videos,
            "youtube": youtube.analysis if youtube else None,
            "youtube_historic": youtube_hist.analysis if youtube_hist else None,
            "youtube_top_videos": youtube_videos,
            "youtube_top_shorts": youtube_shorts,
        }


# ===========================================================================
# Artist (profile) tools
# ===========================================================================
# ---------------------------------------------------------------------------
# Spotify artist
# ---------------------------------------------------------------------------
@tool
def fetch_spotify_artist_stats(artist_id: int) -> dict:
    """Fetch current Spotify profile metrics for an artist."""
    with _db.session() as s:
        row = s.query(SpotifyArtist).filter_by(artist_id=artist_id).one_or_none()
        if row is None:
            return {"error": f"no spotify_artist row for artist_id={artist_id}"}
        return {
            "streams": row.streams,
            "monthly_listeners": row.monthly_listeners,
            "popularity_current": row.popularity_current,
            "followers_total": row.followers_total,
        }


@tool
def fetch_spotify_artist_historic(artist_id: int) -> list[dict]:
    """Fetch the chronological Spotify profile history for an artist (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(SpotifyArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(SpotifyArtistHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "popularity_current": r.popularity_current,
                "followers_total": r.followers_total,
                "monthly_listeners": r.monthly_listeners,
                "streams_total": r.streams_total,
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Instagram artist
# ---------------------------------------------------------------------------
@tool
def fetch_instagram_artist_stats(artist_id: int) -> dict:
    """Fetch current Instagram profile metrics for an artist."""
    with _db.session() as s:
        row = s.query(InstagramArtist).filter_by(artist_id=artist_id).one_or_none()
        if row is None:
            return {"error": f"no instagram_artist row for artist_id={artist_id}"}
        return {
            "video_count": row.video_count,
            "views": row.views,
            "likes": row.likes,
            "comments": row.comments,
            "followers": row.followers,
            "video_reach": row.video_reach,
            "engagement": row.engagement,
        }


@tool
def fetch_instagram_artist_historic(artist_id: int) -> list[dict]:
    """Fetch the chronological Instagram profile history (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(InstagramArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(InstagramArtistHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "video_count": r.video_count,
                "views": r.views,
                "likes": r.likes,
                "comments": r.comments,
                "followers": r.followers,
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# TikTok artist
# ---------------------------------------------------------------------------
@tool
def fetch_tiktok_artist_stats(artist_id: int) -> dict:
    """Fetch current TikTok profile metrics for an artist."""
    with _db.session() as s:
        row = s.query(TiktokArtist).filter_by(artist_id=artist_id).one_or_none()
        if row is None:
            return {"error": f"no tiktok_artist row for artist_id={artist_id}"}
        return {
            "video_count": row.video_count,
            "views": row.views,
            "likes": row.likes,
            "shares": row.shares,
            "comments": row.comments,
            "followers": row.followers,
            "profile_likes": row.profile_likes,
            "video_reach": row.video_reach,
            "engagement": row.engagement,
        }


@tool
def fetch_tiktok_artist_historic(artist_id: int) -> list[dict]:
    """Fetch the chronological TikTok profile history (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(TiktokArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(TiktokArtistHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "video_count": r.video_count,
                "views": r.views,
                "likes": r.likes,
                "shares": r.shares,
                "comments": r.comments,
                "followers": r.followers,
                "profile_likes": r.profile_likes,
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# YouTube artist
# ---------------------------------------------------------------------------
@tool
def fetch_youtube_artist_stats(artist_id: int) -> dict:
    """Fetch current YouTube profile metrics for an artist."""
    with _db.session() as s:
        row = s.query(YoutubeArtist).filter_by(artist_id=artist_id).one_or_none()
        if row is None:
            return {"error": f"no youtube_artist row for artist_id={artist_id}"}
        return {
            "creator_reach": row.creator_reach,
            "subscribers": row.subscribers,
            "channel_views": row.channel_views,
            "engagement": row.engagement,
            "video_count": row.video_count,
            "video_views": row.video_views,
            "video_likes": row.video_likes,
            "video_comments": row.video_comments,
            "video_reach": row.video_reach,
            "shorts_count": row.shorts_count,
            "shorts_views": row.shorts_views,
            "shorts_likes": row.shorts_likes,
            "shorts_comments": row.shorts_comments,
        }


@tool
def fetch_youtube_artist_historic(artist_id: int) -> list[dict]:
    """Fetch the chronological YouTube profile history (oldest first)."""
    with _db.session() as s:
        rows = (
            s.query(YoutubeArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(YoutubeArtistHistoric.date.asc())
            .all()
        )
        return [
            {
                "date": _iso(r.date),
                "subscribers": r.subscribers,
                "views": r.views,
                "likes": r.likes,
                "comments": r.comments,
            }
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Artist summary helper
# ---------------------------------------------------------------------------
@tool
def fetch_all_artist_analyses(artist_id: int) -> dict:
    """Fetch every per-platform analysis already stored for an artist."""
    with _db.session() as s:
        artist = s.query(Artist).filter_by(id=artist_id).one_or_none()
        if artist is None:
            return {"error": f"no artist row for artist_id={artist_id}"}

        spotify = s.query(SpotifyArtist).filter_by(artist_id=artist_id).one_or_none()
        spotify_hist = (
            s.query(SpotifyArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(SpotifyArtistHistoric.date.desc())
            .first()
        )
        instagram = (
            s.query(InstagramArtist).filter_by(artist_id=artist_id).one_or_none()
        )
        instagram_hist = (
            s.query(InstagramArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(InstagramArtistHistoric.date.desc())
            .first()
        )
        tiktok = s.query(TiktokArtist).filter_by(artist_id=artist_id).one_or_none()
        tiktok_hist = (
            s.query(TiktokArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(TiktokArtistHistoric.date.desc())
            .first()
        )
        youtube = s.query(YoutubeArtist).filter_by(artist_id=artist_id).one_or_none()
        youtube_hist = (
            s.query(YoutubeArtistHistoric)
            .filter_by(artist_id=artist_id)
            .order_by(YoutubeArtistHistoric.date.desc())
            .first()
        )

        return {
            "name": artist.name,
            "spotify": spotify.analysis if spotify else None,
            "spotify_historic": spotify_hist.analysis if spotify_hist else None,
            "instagram": instagram.analysis if instagram else None,
            "instagram_historic": instagram_hist.analysis if instagram_hist else None,
            "tiktok": tiktok.analysis if tiktok else None,
            "tiktok_historic": tiktok_hist.analysis if tiktok_hist else None,
            "youtube": youtube.analysis if youtube else None,
            "youtube_historic": youtube_hist.analysis if youtube_hist else None,
        }
