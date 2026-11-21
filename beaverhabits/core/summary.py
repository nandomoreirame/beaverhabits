"""Pure helpers for habit summaries used by the extended API."""

import datetime
from collections.abc import Iterable

ONE_DAY = datetime.timedelta(days=1)


def current_streak(days: Iterable[datetime.date], today: datetime.date) -> int:
    """Consecutive done days ending today, or yesterday while today is still open."""
    done = set(days)
    cursor = today if today in done else today - ONE_DAY
    streak = 0
    while cursor in done:
        streak += 1
        cursor -= ONE_DAY
    return streak


def longest_streak(days: Iterable[datetime.date], today: datetime.date) -> int:
    """Longest run of consecutive done days up to and including today."""
    best = run = 0
    previous: datetime.date | None = None
    for day in sorted(d for d in set(days) if d <= today):
        run = run + 1 if previous is not None and day - previous == ONE_DAY else 1
        best = max(best, run)
        previous = day
    return best


def count_between(
    days: Iterable[datetime.date], start: datetime.date, end: datetime.date
) -> int:
    """Number of done days in the inclusive range [start, end]."""
    return sum(1 for day in set(days) if start <= day <= end)
