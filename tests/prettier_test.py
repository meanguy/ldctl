from datetime import timedelta

import pytest

from ldctl.prettier import parse_time_ago


@pytest.mark.parametrize(
    ("s", "expected"),
    [
        ("1d", timedelta(days=1)),
        ("1d2h", timedelta(days=1, hours=2)),
        ("1 day", timedelta(days=1)),
        ("1 days", timedelta(days=1)),
        ("1 day 2 hours", timedelta(days=1, hours=2)),
        ("1 day 2 hours 3 minutes", timedelta(days=1, hours=2, minutes=3)),
        ("1 day 2 hours 3 minutes 4 seconds", timedelta(days=1, hours=2, minutes=3, seconds=4)),
        (
            "1 day 2 hours 3 minutes 4 seconds 5 milliseconds",
            timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=5),
        ),
        (
            "1 day 2 hours 3 minutes 4 seconds 5 milliseconds 6 microseconds",
            timedelta(days=1, hours=2, minutes=3, seconds=4, milliseconds=5, microseconds=6),
        ),
        ("3 years", timedelta(days=3 * 365)),
        ("3 years 2 months", timedelta(days=3 * 365 + 2 * 30)),
        ("2 weeks", timedelta(weeks=2)),
    ],
)
def test_parse_time_ago(s, expected):
    assert parse_time_ago(s) == expected
