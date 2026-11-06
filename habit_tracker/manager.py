"""Application logic: the only layer the user interface talks to.

The manager validates input, applies the rules (unique names, one completion per
period) and delegates storage to the repository. It never prints anything.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union

from .habit import Habit, Periodicity
from .repository import HabitRepository


class HabitError(Exception):
    """A problem the user can fix (empty name, unknown habit, duplicate name ...)."""


class HabitManager:
    """Create, complete, delete and list habits."""

    def __init__(self, repository: HabitRepository) -> None:
        self._repo = repository

    def habit_exists(self, name: str) -> bool:
        """Return True if a habit with this name exists (case-insensitive)."""
        return self._repo.get_by_name(name) is not None

    def create_habit(self, name: str, description: str,
                     periodicity: Union[Periodicity, str]) -> Habit:
        """Create and store a new habit.

        Args:
            periodicity: a ``Periodicity`` or the text 'daily' / 'weekly'.

        Raises:
            HabitError: for an empty name, an invalid periodicity or a duplicate name.
        """
        if isinstance(periodicity, str):
            try:
                periodicity = Periodicity.from_text(periodicity)
            except ValueError as err:
                raise HabitError(str(err)) from None
        try:
            habit = Habit(name, description, periodicity)
        except ValueError as err:
            raise HabitError(str(err)) from None
        if self.habit_exists(habit.name):
            raise HabitError(f"A habit called '{habit.name}' already exists.")
        self._repo.add_habit(habit)
        return habit

    def get_habit(self, name: str) -> Habit:
        """Return the habit with this name or raise ``HabitError`` if it does not exist."""
        habit = self._repo.get_by_name(name)
        if habit is None:
            raise HabitError(f"No habit called '{name.strip()}' found.")
        return habit

    def complete_habit(self, name: str, when: Optional[datetime] = None) -> bool:
        """Check a habit off.

        Returns:
            True if the completion was stored; False if the habit was already
            completed in the current period.
        """
        habit = self.get_habit(name)
        when = when or datetime.now()
        if not habit.complete(when):
            return False
        self._repo.add_completion(habit, when)
        return True

    def delete_habit(self, name: str) -> None:
        """Delete a habit and its history (raises ``HabitError`` if it does not exist)."""
        habit = self.get_habit(name)
        self._repo.delete_habit(habit.name)

    def list_habits(self) -> List[Habit]:
        """Return all habits, oldest first."""
        return self._repo.get_all()
