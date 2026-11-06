"""Command line interface: menu, user input and screen output only.

No business logic lives here. Every action is delegated to the ``HabitManager``
(create, complete, delete, list) or to the pure functions in ``analytics``.
Problems the user can fix are reported with ``HabitError`` and printed by ``run``.
"""
from __future__ import annotations

from . import analytics
from .habit import Periodicity
from .manager import HabitError, HabitManager

MENU = """
=== HABIT TRACKER ===
  1) Create a habit
  2) Complete a habit
  3) List my habits
  4) Analyse my habits
  5) Delete a habit
  6) Exit
"""


def _ask(prompt: str) -> str:
    """Read one line from the user and strip surrounding spaces."""
    return input(prompt).strip()


def _ask_periodicity() -> Periodicity:
    """Ask until the user enters daily/weekly (or the shortcuts d/w)."""
    while True:
        answer = _ask("How often? (daily / weekly): ").lower()
        answer = {"d": "daily", "w": "weekly"}.get(answer, answer)
        try:
            return Periodicity.from_text(answer)
        except ValueError as err:
            print(f"Error: {err}")


def _select_habit(manager: HabitManager, prompt: str) -> str:
    """Let the user choose a habit by its number in the list or by its name.

    Returns the name (the manager checks that it exists).
    """
    answer = _ask(prompt)
    if answer.isdigit():
        habits = manager.list_habits()
        number = int(answer)
        if 1 <= number <= len(habits):
            return habits[number - 1].name
        raise HabitError(f"There is no habit number {number}.")
    return answer


def create_habit_ui(manager: HabitManager) -> None:
    """Menu option 1: ask for name, description and period, then create the habit."""
    name = _ask("Name of the habit: ")
    if not name:
        raise HabitError("A habit needs a name.")
    if manager.habit_exists(name):
        raise HabitError(f"A habit called '{name}' already exists.")
    description = _ask("Short description (optional): ")
    periodicity = _ask_periodicity()
    habit = manager.create_habit(name, description, periodicity)
    print(f"Created {habit.periodicity.value} habit '{habit.name}'.")


def list_habits_ui(manager: HabitManager) -> None:
    """Menu option 3: print all habits and whether they are done in the current period."""
    habits = manager.list_habits()
    if not habits:
        print("You have no habits yet.")
        return
    print(f"\n{'No.':<5}{'Habit':<22}{'Period':<9}{'Done now?':<11}Description")
    print("-" * 69)
    for number, h in enumerate(habits, start=1):
        status = "yes" if h.is_completed_in() else "no"
        print(f"{number:<5}{h.name:<22}{h.periodicity.value:<9}{status:<11}{h.description}")


def complete_habit_ui(manager: HabitManager) -> None:
    """Menu option 2: show the habits and check one off."""
    if not manager.list_habits():
        print("You have no habits yet. Create one first.")
        return
    list_habits_ui(manager)
    name = _select_habit(manager, "Which habit did you complete? (number or name): ")
    if manager.complete_habit(name):
        print(f"Well done! '{manager.get_habit(name).name}' checked off.")
    else:
        print("You already completed this habit in the current period.")


def show_analytics_ui(manager: HabitManager) -> None:
    """Menu option 4: streaks and completion rate, optionally filtered by period."""
    habits = manager.list_habits()
    if not habits:
        print("Nothing to analyse yet.")
        return
    choice = _ask("Show (a)ll, (d)aily or (w)eekly habits? [a]: ").lower() or "a"
    if choice.startswith("d"):
        habits = analytics.filter_by_periodicity(habits, Periodicity.DAILY)
    elif choice.startswith("w"):
        habits = analytics.filter_by_periodicity(habits, Periodicity.WEEKLY)
    if not habits:
        print("No habits of this type yet.")
        return
    print(f"\n{'Habit':<22}{'Period':<9}{'Current':>8}{'Longest':>9}{'Rate':>7}")
    print("-" * 55)
    for name, period, current, longest, rate in analytics.summarise(habits):
        print(f"{name:<22}{period:<9}{current:>8}{longest:>9}{rate:>7.0%}")
    best = analytics.longest_streak_all(habits)
    if best:
        unit = "days" if best[0].periodicity is Periodicity.DAILY else "weeks"
        print(f"\nLongest streak overall: '{best[0].name}' with {best[1]} {unit}.")


def delete_habit_ui(manager: HabitManager) -> None:
    """Menu option 5: delete a habit (and its history) after a confirmation."""
    name = _select_habit(manager, "Number or name of the habit to delete: ")
    habit = manager.get_habit(name)          # fails early if the habit does not exist
    if _ask(f"Really delete '{habit.name}' and all its history? (y/n): ").lower() == "y":
        manager.delete_habit(habit.name)
        print("Habit deleted.")
    else:
        print("Nothing was deleted.")


ACTIONS = {"1": create_habit_ui, "2": complete_habit_ui, "3": list_habits_ui,
           "4": show_analytics_ui, "5": delete_habit_ui}


def run(manager: HabitManager) -> None:
    """Main menu loop; runs until the user chooses 6 (or presses Ctrl+C / Ctrl+D)."""
    while True:
        print(MENU)
        try:
            choice = _ask("Choose an option (1-6): ")
            if choice == "6":
                print("Goodbye!")
                return
            action = ACTIONS.get(choice)
            if action is None:
                print("Please enter a number from 1 to 6.")
                continue
            action(manager)
        except HabitError as err:        # problems the user can fix: show and continue
            print(f"Error: {err}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return
