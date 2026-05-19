"""Calendar-context tools for the Period Track Analyzer agent.

Provides today's date, the track's basic identity (title + release date), and
a list of cultural/seasonal anchors resolved against today so the agent can
reason about the 90-day pre-peak work window.
"""

from __future__ import annotations

import calendar
from datetime import date

from strands import tool

from src.db import Database, Track
from src.utils import parse_date

_db = Database()


# ---------------------------------------------------------------------------
# Cultural / seasonal calendar (Western / EU market)
# ---------------------------------------------------------------------------
# Each entry is (name, peak_start "MM-DD", peak_end "MM-DD"). For windows that
# straddle Dec 31 (e.g. New Year), `peak_end` is set to the early-January date
# and resolution treats it as next year automatically.
_ANCHORS: list[tuple[str, str, str]] = [
    ("Valentine's Day", "02-14", "02-14"),
    ("Spring", "03-21", "05-31"),
    ("Festival season EU", "05-15", "08-31"),
    ("Summer", "06-21", "08-31"),
    ("Back-to-school", "09-01", "09-15"),
    ("Autumn", "09-22", "11-30"),
    ("Halloween", "10-25", "10-31"),
    ("Christmas", "12-01", "12-25"),
    ("New Year", "12-26", "01-05"),
]


def _resolve_md(md: str, today: date, anchor_for_year: int) -> date:
    """Turn an "MM-DD" string into a date in `anchor_for_year`."""
    return parse_date(f"{anchor_for_year:04d}-{md}")


def _next_occurrence(peak_start_md: str, peak_end_md: str, today: date) -> tuple[date, date]:
    """Pick the most relevant (start, end) pair: the current/upcoming occurrence.

    If today is already past this year's `peak_end`, roll the anchor to next
    year. For wrap-around anchors (start > end as MM-DD strings), end belongs
    to the following calendar year.
    """
    year = today.year
    wraps = peak_start_md > peak_end_md
    start = _resolve_md(peak_start_md, today, year)
    end = _resolve_md(peak_end_md, today, year + 1 if wraps else year)
    if end < today:
        start = _resolve_md(peak_start_md, today, year + 1)
        end = _resolve_md(peak_end_md, today, year + 2 if wraps else year + 1)
    return start, end


@tool
def fetch_track_basics(track_id: int) -> dict:
    """Fetch the track's title, release date, and age in days.

    Returns a JSON-serialisable dict. `days_since_release` is negative when the
    release date is in the future. Returns `{"error": ...}` if the track is
    missing or has no release date set when needed.
    """
    with _db.session() as s:
        row = s.query(Track).filter_by(id=track_id).one_or_none()
        if row is None:
            return {"error": f"no track row for track_id={track_id}"}
        release = row.release_date
        days_since = (date.today() - release).days if release is not None else None
        return {
            "title": row.title,
            "release_date": release.isoformat() if release is not None else None,
            "days_since_release": days_since,
            "is_released": bool(release is not None and days_since is not None and days_since >= 0),
        }


@tool
def today_info() -> dict:
    """Return today's date plus useful calendar fields."""
    t = date.today()
    return {
        "today": t.isoformat(),
        "year": t.year,
        "month": t.month,
        "month_name": calendar.month_name[t.month],
        "day": t.day,
        "weekday": calendar.day_name[t.weekday()],
        "day_of_year": t.timetuple().tm_yday,
        "iso_week": t.isocalendar().week,
    }


@tool
def calendar_anchors() -> list[dict]:
    """List cultural/seasonal anchors resolved against today.

    Each anchor includes its next-occurrence peak window and how many days
    away that window starts. `work_window_start_days` is the canonical
    90-day-before-peak marker: zero or negative means the work window is
    already open.
    """
    today = date.today()
    out: list[dict] = []
    for name, peak_start_md, peak_end_md in _ANCHORS:
        start, end = _next_occurrence(peak_start_md, peak_end_md, today)
        days_until_start = (start - today).days
        out.append(
            {
                "name": name,
                "peak_start": start.isoformat(),
                "peak_end": end.isoformat(),
                "days_until_peak_start": days_until_start,
                "in_window_now": start <= today <= end,
                "work_window_start_days": days_until_start - 90,
            }
        )
    return out
