import re
from datetime import timedelta

_TIME_UNITS = {
    ("years", "year", "y"): "years",
    ("days", "day", "d"): "days",
    ("weeks", "week", "w"): "weeks",
    ("minutes", "minute", "m"): "minutes",
    ("months", "month", "M"): "months",
    ("hours", "hour", "h"): "hours",
    ("seconds", "second", "s"): "seconds",
    ("milliseconds", "millisecond", "ms"): "milliseconds",
    ("microseconds", "microsecond", "us"): "microseconds",
}
_TIME_UNITS_MAP = {unit: key for units, key in _TIME_UNITS.items() for unit in units}
_TIME_UNITS_REGEX = re.compile(r"(\d+)\s*([a-zA-Z]+)")


def parse_time_ago(s: str) -> timedelta:
    """
    Parse a time ago string into a timedelta.

    Examples:

        >>> parse_time_ago("1d")
        datetime.timedelta(days=1)

        >>> parse_time_ago("1 day")
        datetime.timedelta(days=1)

        >>> parse_time_ago("1 days")
        datetime.timedelta(days=1)

        >>> parse_time_ago("1 day 2 hours")
        datetime.timedelta(days=1, hours=2)

        >>> parse_time_ago("1 day 2 hours 3 minutes")
        datetime.timedelta(days=1, hours=2, minutes=3)

        >>> parse_time_ago("1 day 2 hours 3 minutes 4 seconds")
        datetime.timedelta(days=1, hours=2, minutes=3, seconds=4)

        >>> parse_time_ago("1 day 2 hours 3 minutes 4 seconds 5 milliseconds")
        datetime.timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=5)

        >>> parse_time_ago("1 day 2 hours 3 minutes 4 seconds 5 milliseconds 6 microseconds")
        datetime.timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=5, microseconds=6)
    """
    s = s.strip()

    if not s:
        raise ValueError("empty string")

    matches = _TIME_UNITS_REGEX.findall(s)
    if not matches:
        raise ValueError("invalid string")

    kwargs = {}
    for match in matches:
        value = int(match[0])
        unit = match[1].lower()

        if unit not in _TIME_UNITS_MAP:
            raise ValueError(f"invalid unit: {unit}")

        if unit not in _TIME_UNITS_MAP:
            raise ValueError(f"invalid unit: {unit}")

        kwargs[_TIME_UNITS_MAP[unit]] = value

    years = kwargs.pop("years", 0)
    months = kwargs.pop("months", 0)

    if years or months:
        days = kwargs.pop("days", 0)
        kwargs["days"] = days + years * 365 + months * 30

    return timedelta(**kwargs)
