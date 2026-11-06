from datetime import datetime

import pytest

from habit_tracker.habit import Habit, Periodicity, period_start


def test_name_is_required():
    with pytest.raises(ValueError):
        Habit("   ")


def test_complete_stores_once_per_day():
    h = Habit("Read", periodicity=Periodicity.DAILY)
    assert h.complete(datetime(2026, 3, 2, 8)) is True
    assert h.complete(datetime(2026, 3, 2, 20)) is False   # same day -> ignored
    assert h.complete(datetime(2026, 3, 3, 8)) is True
    assert len(h.completions) == 2


def test_weekly_period_is_monday_to_sunday():
    monday = datetime(2026, 3, 2, 9)      # Monday
    sunday = datetime(2026, 3, 8, 23)     # Sunday of the same week
    next_monday = datetime(2026, 3, 9, 0, 1)
    assert period_start(monday, Periodicity.WEEKLY) == period_start(sunday, Periodicity.WEEKLY)
    assert period_start(next_monday, Periodicity.WEEKLY) != period_start(sunday, Periodicity.WEEKLY)


def test_periodicity_from_text():
    assert Periodicity.from_text(" Weekly ") is Periodicity.WEEKLY
    with pytest.raises(ValueError):
        Periodicity.from_text("monthly")
