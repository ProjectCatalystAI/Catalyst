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
    Parse a date string in ISO format to a date object.
    :param value: The date string in ISO format (YYYY-MM-DD).
    :returns: A date object, or None if the value is empty.
    """
    if not value:
        return None
    return date.fromisoformat(value.strip())
