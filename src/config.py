import os

from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.environ["LASTFM_API_KEY"]
LASTFM_API_SECRET = os.environ["LASTFM_API_SECRET"]
LASTFM_BASE = "https://ws.audioscrobbler.com/2.0/"

SOUNDCLOUD_BASE = "https://api.soundcloud.com"
SOUNDCLOUD_BASE_V2 = "https://api-v2.soundcloud.com"
