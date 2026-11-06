"""Storage layer: saves and loads habits with SQLite (Python standard library).

Two tables are used: ``habit`` and ``completion`` (one habit has many
completions). All timestamps are stored as ISO-8601 text.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import List, Optional

from .habit import Habit, Periodicity

SCHEMA = """
CREATE TABLE IF NOT EXISTS habit (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
    description TEXT NOT NULL DEFAULT '',
    periodicity TEXT NOT NULL CHECK (periodicity IN ('daily', 'weekly')),
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS completion (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    habit_id     INTEGER NOT NULL REFERENCES habit(id) ON DELETE CASCADE,
    completed_at TEXT NOT NULL
);
"""


class HabitRepository:
    """Translates between database rows and ``Habit`` objects.

    Args:
        db_path: path of the SQLite file, or ``":memory:"`` for a temporary
            database (used by the tests).
    """

    def __init__(self, db_path: str = "habits.db") -> None:
        self.conn = sqlite3.connect(db_path)
        # SQLite ignores foreign keys unless this is switched on for every connection.
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ---------- write operations ----------
    def add_habit(self, habit: Habit) -> None:
        """Insert a new habit together with any completions it already has."""
        with self.conn:  # commits on success, rolls back on error
            cur = self.conn.execute(
                "INSERT INTO habit (name, description, periodicity, created_at) VALUES (?, ?, ?, ?)",
                (habit.name, habit.description, habit.periodicity.value, habit.created_at.isoformat()),
            )
            self.conn.executemany(
                "INSERT INTO completion (habit_id, completed_at) VALUES (?, ?)",
                [(cur.lastrowid, c.isoformat()) for c in habit.completions],
            )

    def add_completion(self, habit: Habit, when: datetime) -> None:
        """Store one completion for a habit that already exists in the database."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO completion (habit_id, completed_at) "
                "SELECT id, ? FROM habit WHERE name = ?",
                (when.isoformat(), habit.name),
            )

    def delete_habit(self, name: str) -> bool:
        """Delete a habit by name; its completions are removed too (ON DELETE CASCADE).

        Returns:
            True if a habit was deleted, False if no habit had this name.
        """
        with self.conn:
            cur = self.conn.execute("DELETE FROM habit WHERE name = ?", (name,))
        return cur.rowcount > 0

    # ---------- read operations ----------
    def get_all(self) -> List[Habit]:
        """Return every habit (oldest first) as ``Habit`` objects including completions."""
        rows = self.conn.execute(
            "SELECT id, name, description, periodicity, created_at FROM habit ORDER BY id"
        ).fetchall()
        return [self._build(row) for row in rows]

    def get_by_name(self, name: str) -> Optional[Habit]:
        """Return the habit with this name (case-insensitive) or ``None``."""
        row = self.conn.execute(
            "SELECT id, name, description, periodicity, created_at FROM habit WHERE name = ?",
            (name.strip(),),
        ).fetchone()
        return self._build(row) if row else None

    def _build(self, row: tuple) -> Habit:
        """Create a ``Habit`` object from one ``habit`` row plus its completion rows."""
        habit_id, name, description, periodicity, created_at = row
        completions = [
            datetime.fromisoformat(r[0])
            for r in self.conn.execute(
                "SELECT completed_at FROM completion WHERE habit_id = ? ORDER BY completed_at",
                (habit_id,),
            )
        ]
        return Habit(name, description, Periodicity(periodicity),
                     datetime.fromisoformat(created_at), completions)

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()
