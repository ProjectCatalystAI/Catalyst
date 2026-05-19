"""
Starting point to import catalogue.csv into the database and verify
that all tables are correctly populated.

Usage:
    python import_catalogue.py

The script reads catalogue.csv from the project root, populates the database
(catalyst.db), and prints a summary of what was loaded for each track.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from db import Database
from load_catalogue import load_catalog_from_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(name)s  %(message)s",
)

CSV_PATH = Path(__file__).parent / "catalogue.csv"
DB_URL = f"sqlite:///{Path(__file__).parent / 'catalyst.db'}"


def main() -> None:
    db = Database(DB_URL)
    print(f"Importing '{CSV_PATH.name}' …")
    catalog = load_catalog_from_csv(CSV_PATH, db)
    print(f"\nCatalog created: '{catalog.name}' (id={catalog.id})")

    with db.session() as session:
        from db import (
            Track, Artist,
            SpotifyArtist, InstagramArtist, TiktokArtist, YoutubeArtist,
            SpotifyTrack, InstagramTrack, TiktokTrack, YoutubeTrack,
            SpotifyTrackHistoric, InstagramTrackHistoric,
            TiktokTrackHistoric, YoutubeTrackHistoric,
            InstagramVideoTrack, TiktokVideoTrack,
            YoutubeVideoTrack, YoutubeShortTrack,
        )

        tracks = (
            session.query(Track)
            .filter_by(catalog_id=catalog.id)
            .all()
        )

        print(f"\n{'─' * 60}")
        for track in tracks:
            artist = session.get(Artist, track.artist_id)
            print(f"\nTrack : {track.title}")
            print(f"Artist: {artist.name}  (spotify_id={artist.spotify_id})")
            print(f"  ISRC        : {track.isrc}")
            print(f"  country     : {artist.country}")
            print(f"  bio         : {'yes' if artist.bio else 'no'}")

            sp_a = session.query(SpotifyArtist).filter_by(artist_id=artist.id).first()
            print(f"  Spotify artist  : monthly_listeners={getattr(sp_a, 'monthly_listeners', '—')}, "
                  f"followers={getattr(sp_a, 'followers_total', '—')}")

            ig_a = session.query(InstagramArtist).filter_by(artist_id=artist.id).first()
            print(f"  Instagram artist: followers={getattr(ig_a, 'followers', '—')}, "
                  f"views={getattr(ig_a, 'views', '—')}")

            tt_a = session.query(TiktokArtist).filter_by(artist_id=artist.id).first()
            print(f"  TikTok artist   : followers={getattr(tt_a, 'followers', '—')}, "
                  f"views={getattr(tt_a, 'views', '—')}")

            yt_a = session.query(YoutubeArtist).filter_by(artist_id=artist.id).first()
            print(f"  YouTube artist  : subscribers={getattr(yt_a, 'subscribers', '—')}, "
                  f"channel_views={getattr(yt_a, 'channel_views', '—')}")

            sp_t = session.query(SpotifyTrack).filter_by(track_id=track.id).first()
            print(f"  Spotify track   : streams={getattr(sp_t, 'streams', '—')}, "
                  f"popularity={getattr(sp_t, 'popularity', '—')}")

            sp_hist = session.query(SpotifyTrackHistoric).filter_by(track_id=track.id).count()
            print(f"  Spotify historic: {sp_hist} rows")

            ig_t = session.query(InstagramTrack).filter_by(track_id=track.id).first()
            ig_hist = session.query(InstagramTrackHistoric).filter_by(track_id=track.id).count()
            ig_vids = (
                session.query(InstagramVideoTrack)
                .filter_by(instagram_track_id=getattr(ig_t, "id", None))
                .count()
                if ig_t else 0
            )
            print(f"  Instagram track : views={getattr(ig_t, 'views', '—')}, "
                  f"historic={ig_hist} rows, videos={ig_vids}")

            tt_t = session.query(TiktokTrack).filter_by(track_id=track.id).first()
            tt_hist = session.query(TiktokTrackHistoric).filter_by(track_id=track.id).count()
            tt_vids = (
                session.query(TiktokVideoTrack)
                .filter_by(tiktok_track_id=getattr(tt_t, "id", None))
                .count()
                if tt_t else 0
            )
            print(f"  TikTok track    : views={getattr(tt_t, 'views', '—')}, "
                  f"historic={tt_hist} rows, videos={tt_vids}")

            yt_t = session.query(YoutubeTrack).filter_by(track_id=track.id).first()
            yt_hist = session.query(YoutubeTrackHistoric).filter_by(track_id=track.id).count()
            yt_vids = (
                session.query(YoutubeVideoTrack)
                .filter_by(youtube_track_id=getattr(yt_t, "id", None))
                .count()
                if yt_t else 0
            )
            yt_shorts = (
                session.query(YoutubeShortTrack)
                .filter_by(youtube_track_id=getattr(yt_t, "id", None))
                .count()
                if yt_t else 0
            )
            print(f"  YouTube track   : views={getattr(yt_t, 'video_views', '—')}, "
                  f"historic={yt_hist} rows, videos={yt_vids}, shorts={yt_shorts}")

        print(f"\n{'─' * 60}")
        print("Done.")


if __name__ == "__main__":
    main()
