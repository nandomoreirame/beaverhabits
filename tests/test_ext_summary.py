from datetime import date, timedelta

from beaverhabits.core.summary import count_between, current_streak, longest_streak

TODAY = date(2026, 11, 21)


def days_back(*offsets: int) -> set[date]:
    return {TODAY - timedelta(days=n) for n in offsets}


def test_current_streak_counts_consecutive_days_ending_today():
    assert current_streak(days_back(0, 1, 2, 4), TODAY) == 3


def test_current_streak_stays_alive_when_today_is_not_done_yet():
    assert current_streak(days_back(1, 2), TODAY) == 2


def test_current_streak_is_zero_after_a_missed_day():
    assert current_streak(days_back(2, 3), TODAY) == 0


def test_current_streak_ignores_future_days():
    assert current_streak({TODAY + timedelta(days=1)} | days_back(0), TODAY) == 1


def test_current_streak_empty():
    assert current_streak(set(), TODAY) == 0


def test_longest_streak_finds_best_run_up_to_today():
    days = days_back(0, 1, 5, 6, 7, 8) | {TODAY + timedelta(days=1)}
    assert longest_streak(days, TODAY) == 4


def test_longest_streak_empty():
    assert longest_streak(set(), TODAY) == 0


def test_count_between_is_inclusive():
    days = days_back(0, 3, 6, 7)
    assert count_between(days, TODAY - timedelta(days=6), TODAY) == 3
