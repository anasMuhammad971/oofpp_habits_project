"""Analytics written in a functional style.

Every function here is PURE: it only reads its arguments and returns a new
value. Nothing is printed, stored or changed, so the functions are easy to test
and to combine. Functional tools used: ``map``, ``filter``, ``functools.reduce``,
``sorted``, set comprehensions and ``lambda``.

Vocabulary:
    period       one day (daily habits) or one ISO week (weekly habits)
    period key   the first day of a period, see ``habit.period_start``
    streak       number of consecutive periods in which a habit was completed
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from functools import reduce
from typing import List, Optional, Sequence, Tuple

from .habit import Habit, Periodicity, period_length, period_start


def period_keys(habit: Habit) -> List[date]:
    """Sorted list of the distinct periods in which the habit was completed."""
    return sorted({period_start(c, habit.periodicity) for c in habit.completions})


def _runs(keys: Sequence[date], step: timedelta) -> List[List[date]]:
    """Split sorted period keys into runs of consecutive periods using ``reduce``.

    Example (daily): ``[d1, d2, d3, d5]`` becomes ``[[d1, d2, d3], [d5]]``.
    """
    def fold(runs: List[List[date]], key: date) -> List[List[date]]:
        if runs and key - runs[-1][-1] == step:
            return runs[:-1] + [runs[-1] + [key]]   # key continues the last run
        return runs + [[key]]                        # gap found: start a new run
    return reduce(fold, keys, [])


def longest_streak(habit: Habit) -> int:
    """Longest number of consecutive periods in which the habit was completed."""
    runs = _runs(period_keys(habit), period_length(habit.periodicity))
    return max(map(len, runs), default=0)


def current_streak(habit: Habit, today: Optional[datetime] = None) -> int:
    """Length of the streak that is still alive (0 if it is broken).

    A streak is alive if its last period is the current period or the one before
    it, because the user still has time to complete the current period.
    """
    step = period_length(habit.periodicity)
    runs = _runs(period_keys(habit), step)
    if not runs:
        return 0
    this_period = period_start(today or datetime.now(), habit.periodicity)
    return len(runs[-1]) if runs[-1][-1] >= this_period - step else 0


def completion_rate(habit: Habit, today: Optional[datetime] = None) -> float:
    """Share of periods since creation in which the habit was completed (0.0 to 1.0)."""
    step = period_length(habit.periodicity)
    first = period_start(habit.created_at, habit.periodicity)
    last = period_start(today or datetime.now(), habit.periodicity)
    total = (last - first) // step + 1
    done = len(list(filter(lambda k: first <= k <= last, period_keys(habit))))
    return min(done / total, 1.0) if total > 0 else 0.0


def filter_by_periodicity(habits: Sequence[Habit], periodicity: Periodicity) -> List[Habit]:
    """All habits that have the given periodicity."""
    return list(filter(lambda h: h.periodicity is periodicity, habits))


def longest_streak_all(habits: Sequence[Habit]) -> Optional[Tuple[Habit, int]]:
    """Return ``(habit, streak)`` for the longest streak overall, or ``None`` if no habits."""
    if not habits:
        return None
    best = max(habits, key=longest_streak)
    return best, longest_streak(best)


def summarise(habits: Sequence[Habit], today: Optional[datetime] = None
              ) -> List[Tuple[str, str, int, int, float]]:
    """One row per habit: ``(name, periodicity, current streak, longest streak, rate)``."""
    return list(map(lambda h: (h.name, h.periodicity.value, current_streak(h, today),
                               longest_streak(h), completion_rate(h, today)), habits))
