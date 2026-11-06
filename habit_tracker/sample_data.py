"""Example data so the app can be demonstrated right after installation.

The data is created relative to "now", so there is always a recent history.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from .habit import Habit, Periodicity
from .repository import HabitRepository

# Daily habits: days ago on which the habit was NOT done (every other day was done).
_DAILY_MISSES = {
    "Drink water": {9, 10, 20},
    "Read 20 minutes": {2, 3, 4, 12, 13, 21, 22, 23, 24},
    "Meditate": {0, 1, 5, 6, 7, 8, 14, 15, 16, 17, 18, 19},
}
# Weekly habits: weeks ago in which the habit WAS done (0 = this week).
_WEEKLY_DONE = {"Go for a run": {0, 1, 2, 3}, "Clean the apartment": {1, 2, 4}}
_DESCRIPTIONS = {
    "Drink water": "Drink 2 litres of water",
    "Read 20 minutes": "Read a book before bed",
    "Meditate": "10 minutes of quiet breathing",
    "Go for a run": "Run at least 5 km",
    "Clean the apartment": "Weekly deep clean",
}


def build_sample_habits(today: Optional[datetime] = None) -> List[Habit]:
    """Create 5 habits (3 daily, 2 weekly) with four weeks of example completions."""
    today = today or datetime.now()
    created = (today - timedelta(days=28)).replace(hour=0, minute=0, second=0, microsecond=0)
    stamp = today.replace(minute=0, second=0, microsecond=0)  # never later than "now"
    habits = []
    for name, misses in _DAILY_MISSES.items():
        done = [stamp - timedelta(days=d) for d in range(0, 29) if d not in misses]
        habits.append(Habit(name, _DESCRIPTIONS[name], Periodicity.DAILY, created, done))
    for name, weeks in _WEEKLY_DONE.items():
        done = [today - timedelta(weeks=w) for w in sorted(weeks)]
        habits.append(Habit(name, _DESCRIPTIONS[name], Periodicity.WEEKLY, created, done))
    return habits


def load_sample_data(repository: HabitRepository, today: Optional[datetime] = None) -> None:
    """Store the sample habits in the repository."""
    for habit in build_sample_habits(today):
        repository.add_habit(habit)
