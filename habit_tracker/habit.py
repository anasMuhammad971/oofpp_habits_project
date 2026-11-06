"""Domain model: the ``Habit`` class and the ``Periodicity`` enum.

A ``Habit`` only knows about its own data (name, period, completions). It knows
nothing about the database or the user interface, which keeps it easy to test.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional, Union


class Periodicity(Enum):
    """How often a habit has to be completed."""

    DAILY = "daily"
    WEEKLY = "weekly"

    @classmethod
    def from_text(cls, text: str) -> "Periodicity":
        """Convert user text such as ``' Weekly '`` into a ``Periodicity``.

        Raises:
            ValueError: if the text is neither 'daily' nor 'weekly'.
        """
        try:
            return cls(text.strip().lower())
        except ValueError:
            raise ValueError("Periodicity must be 'daily' or 'weekly'.") from None


def period_start(when: Union[date, datetime], periodicity: Periodicity) -> date:
    """Return the first day of the period that contains ``when``.

    * Daily habits: the period is the calendar day itself.
    * Weekly habits: the period is the ISO week (Monday to Sunday), so the
      Monday of that week is returned.

    Two timestamps in the same period always give the same key. This single
    helper lets the same streak algorithm work for daily and weekly habits.
    """
    day = when.date() if isinstance(when, datetime) else when
    if periodicity is Periodicity.WEEKLY:
        return day - timedelta(days=day.weekday())  # weekday(): Monday == 0
    return day


def period_length(periodicity: Periodicity) -> timedelta:
    """Length of one period: 1 day for daily habits, 7 days for weekly habits."""
    return timedelta(days=7) if periodicity is Periodicity.WEEKLY else timedelta(days=1)


class Habit:
    """One habit together with its completion history.

    Attributes:
        name: unique, non-empty name of the habit.
        description: optional free text.
        periodicity: ``Periodicity.DAILY`` or ``Periodicity.WEEKLY``.
        created_at: when the habit was created.
        completions: sorted list of timestamps at which the habit was checked off.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        periodicity: Periodicity = Periodicity.DAILY,
        created_at: Optional[datetime] = None,
        completions: Optional[List[datetime]] = None,
    ) -> None:
        name = (name or "").strip()
        if not name:
            raise ValueError("A habit needs a name.")
        self.name = name
        self.description = (description or "").strip()
        self.periodicity = periodicity
        self.created_at = created_at or datetime.now()
        self.completions: List[datetime] = sorted(completions or [])

    def is_completed_in(self, when: Optional[datetime] = None) -> bool:
        """Return True if the habit was already checked off in the period of ``when``.

        ``when`` defaults to the current time, i.e. "is the habit done right now?".
        """
        key = period_start(when or datetime.now(), self.periodicity)
        return any(period_start(c, self.periodicity) == key for c in self.completions)

    def complete(self, when: Optional[datetime] = None) -> bool:
        """Check the habit off.

        Returns:
            True if a new completion was stored; False if the habit was already
            completed in this period (so a streak can not be inflated).
        """
        when = when or datetime.now()
        if self.is_completed_in(when):
            return False
        self.completions.append(when)
        self.completions.sort()
        return True

    def __repr__(self) -> str:
        return f"Habit({self.name!r}, {self.periodicity.value}, {len(self.completions)} completions)"
