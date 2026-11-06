"""Tests for the command line interface using scripted keyboard input."""
import builtins
from datetime import datetime, timedelta

import pytest

from habit_tracker import cli
from habit_tracker.habit import Habit, Periodicity
from habit_tracker.manager import HabitManager
from habit_tracker.repository import HabitRepository


@pytest.fixture
def manager():
    repo = HabitRepository(":memory:")
    yield HabitManager(repo)
    repo.close()


def run_menu(monkeypatch, manager, answers):
    """Run the menu loop with a fixed list of typed answers (the last one should be '6')."""
    typed = iter(answers)

    def fake_input(prompt=""):
        try:
            return next(typed)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr(builtins, "input", fake_input)
    cli.run(manager)


def test_create_habit_asks_again_for_invalid_periodicity(monkeypatch, capsys, manager):
    run_menu(monkeypatch, manager, ["1", "Run", "5 km", "monthly", "w", "6"])
    out = capsys.readouterr().out
    assert "Periodicity must be 'daily' or 'weekly'." in out
    assert manager.get_habit("Run").periodicity is Periodicity.WEEKLY


def test_create_rejects_empty_and_duplicate_names(monkeypatch, capsys, manager):
    manager.create_habit("Read", "", "daily")
    run_menu(monkeypatch, manager, ["1", "", "1", "read", "6"])
    out = capsys.readouterr().out
    assert "A habit needs a name." in out
    assert "already exists" in out
    assert len(manager.list_habits()) == 1


def test_complete_by_number_and_duplicate_message(monkeypatch, capsys, manager):
    manager.create_habit("Read", "", "daily")
    run_menu(monkeypatch, manager, ["2", "1", "2", "1", "6"])
    out = capsys.readouterr().out
    assert "checked off" in out
    assert "already completed" in out
    assert len(manager.get_habit("Read").completions) == 1


def test_complete_unknown_habit_or_number(monkeypatch, capsys, manager):
    manager.create_habit("Read", "", "daily")
    run_menu(monkeypatch, manager, ["2", "Nope", "2", "7", "6"])
    out = capsys.readouterr().out
    assert "No habit called 'Nope' found." in out
    assert "There is no habit number 7." in out


def test_delete_cancel_then_confirm(monkeypatch, capsys, manager):
    manager.create_habit("Read", "", "daily")
    run_menu(monkeypatch, manager, ["5", "Read", "n", "5", "1", "y", "6"])
    out = capsys.readouterr().out
    assert "Nothing was deleted." in out and "Habit deleted." in out
    assert manager.list_habits() == []


def test_delete_unknown_habit_fails_before_asking(monkeypatch, capsys, manager):
    run_menu(monkeypatch, manager, ["5", "Ghost", "6"])
    assert "No habit called 'Ghost' found." in capsys.readouterr().out


def test_analytics_filter_weekly_only(monkeypatch, capsys, manager):
    now = datetime.now()
    repo = manager._repo
    repo.add_habit(Habit("Daily one", "", Periodicity.DAILY, now - timedelta(days=3), [now]))
    repo.add_habit(Habit("Weekly one", "", Periodicity.WEEKLY, now - timedelta(days=3), [now]))
    run_menu(monkeypatch, manager, ["4", "w", "6"])
    out = capsys.readouterr().out
    assert "Weekly one" in out and "Daily one" not in out
    assert "Longest streak overall: 'Weekly one' with 1 weeks." in out


def test_empty_tracker_messages(monkeypatch, capsys, manager):
    run_menu(monkeypatch, manager, ["3", "4", "2", "6"])
    out = capsys.readouterr().out
    assert "You have no habits yet." in out
    assert "Nothing to analyse yet." in out


def test_invalid_menu_option_and_ctrl_d(monkeypatch, capsys, manager):
    run_menu(monkeypatch, manager, ["9"])        # then the input ends (EOFError)
    out = capsys.readouterr().out
    assert "Please enter a number from 1 to 6." in out
    assert "Goodbye!" in out
