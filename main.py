"""Start the Habit Tracker.

Usage:
    python main.py              start with habits.db (sample data is loaded on first start)
    python main.py --empty      start without sample data
    python main.py --db my.db   use another database file
"""
import argparse

from habit_tracker.cli import run
from habit_tracker.manager import HabitManager
from habit_tracker.repository import HabitRepository
from habit_tracker.sample_data import load_sample_data


def main() -> None:
    """Parse the options, connect the layers (repository -> manager -> CLI) and run the menu."""
    parser = argparse.ArgumentParser(description="Habit Tracker")
    parser.add_argument("--db", default="habits.db", help="path of the SQLite database file")
    parser.add_argument("--empty", action="store_true", help="do not load sample data")
    args = parser.parse_args()

    repo = HabitRepository(args.db)
    if not args.empty and not repo.get_all():      # only fill a completely empty database
        load_sample_data(repo)
    try:
        run(HabitManager(repo))
    finally:
        repo.close()


if __name__ == "__main__":
    main()
