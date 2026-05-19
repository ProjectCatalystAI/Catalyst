"""
================================================================================
Utils
================================================================================

File structure:

* Date
    * date_until
    * parse_date
"""

from datetime import date


# ================================================================================
# Date
# ================================================================================
def days_until(target: str) -> int:
    """
    Calculate the number of days between today and a target date.
    :param target: The target date in ISO format (YYYY-MM-DD).
    :returns: The number of days until the target date.
    """
    target_date = parse_date(target)
    delta = (target_date - date.today()).days
    return delta


def parse_date(value: str) -> date | None:
    """
    Parse a date string to a date object.
    :param value: Date string in YYYY-MM-DD, YYYY-MM, or YYYY format.
    :returns: A date object, or None if the value is empty or unparseable.
    """
    if not value:
        return None
    v = value.strip()
    parts = v.split("-")
    try:
        if len(parts) == 1:
            return date(int(parts[0]), 1, 1)
        if len(parts) == 2:
            return date(int(parts[0]), int(parts[1]), 1)
        return date.fromisoformat(v)
    except (ValueError, TypeError):
        return None
