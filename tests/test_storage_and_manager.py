from datetime import datetime

import pytest

from habit_tracker.habit import Habit, Periodicity
from habit_tracker.manager import HabitError, HabitManager
from habit_tracker.repository import HabitRepository
from habit_tracker.sample_data import load_sample_data


@pytest.fixture
def repo():
    r = HabitRepository(":memory:")     # temporary database, nothing is written to disk
    yield r
    r.close()


@pytest.fixture
def manager(repo):
    return HabitManager(repo)


def test_repository_roundtrip(repo):
    h = Habit("Run", "5 km", Periodicity.WEEKLY, completions=[datetime(2026, 3, 2, 7)])
    repo.add_habit(h)
    loaded = repo.get_by_name("run")                       # case-insensitive
    assert loaded.name == "Run" and loaded.periodicity is Periodicity.WEEKLY
    assert loaded.completions == [datetime(2026, 3, 2, 7)]


def test_delete_removes_completions_too(repo):
    repo.add_habit(Habit("Run", completions=[datetime(2026, 3, 2, 7)]))
    assert repo.delete_habit("Run") is True
    assert repo.conn.execute("SELECT COUNT(*) FROM completion").fetchone()[0] == 0


def test_manager_create_and_validation(manager):
    manager.create_habit("Read", "", "daily")
    with pytest.raises(HabitError):
        manager.create_habit("read", "", "daily")          # duplicate (case-insensitive)
    with pytest.raises(HabitError):
        manager.create_habit("", "", "daily")              # empty name
    with pytest.raises(HabitError):
        manager.create_habit("X", "", "monthly")           # bad periodicity


def test_manager_complete_persists(manager):
    manager.create_habit("Read", "", "daily")
    assert manager.complete_habit("Read", datetime(2026, 3, 2, 8)) is True
    assert manager.complete_habit("Read", datetime(2026, 3, 2, 9)) is False
    assert len(manager.get_habit("Read").completions) == 1


def test_manager_unknown_habit(manager):
    with pytest.raises(HabitError):
        manager.complete_habit("Nope")


def test_sample_data(repo):
    load_sample_data(repo, datetime(2026, 3, 18, 12))
    habits = repo.get_all()
    assert len(habits) == 5
    assert all(h.completions for h in habits)
