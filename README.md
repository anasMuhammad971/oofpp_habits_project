# Habit Tracker

A command line application to create, complete and analyse **daily** and **weekly** habits.
Written in Python 3 (standard library only) for the course
*Object Oriented and Functional Programming with Python (DLBDSOOFPP01)*, IU International University of Applied Sciences.

**Author:** Anas Muhammad Ismail (matriculation no. 4235232)

## Features
- **Create** habits with a name, a description and a period (daily or weekly)
- **Complete** habits by number or name; a second check-off in the same period is ignored, so streaks cannot be inflated
- **List** all habits and see which ones are already done in the current period
- **Analyse** habits: current streak, longest streak, completion rate, filter by daily/weekly, and the habit with the longest streak overall
- **Delete** a habit and its whole history (with a confirmation question)
- **Persistent storage** in a local SQLite file, so data survives restarts
- **Sample data:** 5 habits with 4 weeks of history are loaded on the first start
- **Friendly input handling:** invalid input is explained and asked again; the program does not crash

## Requirements
- Python 3.9 or newer (check with `python --version`; on some systems the command is `python3` or `py`)
- Nothing else for the application itself. `pytest` is only needed to run the tests.

## Installation
```bash
# 1. get the code
git clone https://github.com/anasMuhammad971/oofpp_habits_project.git
cd oofpp_habits_project

# 2. (optional) install pytest to run the tests
pip install -r requirements.txt
```
No GitHub? Download the repository as a ZIP file, unzip it and open a terminal in the unzipped folder.

## Usage
```bash
python main.py              # normal start (sample data is loaded if the database is empty)
python main.py --empty      # start without sample data
python main.py --db my.db   # use a different database file
```
The app opens a numbered menu. Type a number and press Enter:

```
=== HABIT TRACKER ===
  1) Create a habit
  2) Complete a habit
  3) List my habits
  4) Analyse my habits
  5) Delete a habit
  6) Exit
```

| Option | What happens |
|---|---|
| 1 Create | Enter a name, an optional description and `daily` or `weekly` (`d` / `w` also work). Empty or duplicate names are refused. |
| 2 Complete | The habits are listed with numbers. Enter the number or the name. |
| 3 List | Shows every habit and whether it is done in the current period. |
| 4 Analyse | Choose all, daily or weekly. Shows current streak, longest streak and completion rate. |
| 5 Delete | Enter number or name, then confirm with `y`. |
| 6 Exit | Closes the program. |

> **Tip:** Run the app with `python main.py` in a terminal. Menu numbers are typed *inside* the app, not at the shell prompt.

### Example: analysis
```
Habit                 Period    Current  Longest   Rate
-------------------------------------------------------
Drink water           daily           9        9    90%
Go for a run          weekly          4        4    80%

Longest streak overall: 'Drink water' with 9 days.
```
The numbers depend on the current date because the sample data is created relative to "today".

## How streaks are calculated
A *period* is one day (daily habits) or one ISO week, Monday to Sunday (weekly habits).
1. Every completion is mapped to its period key (the day, or the Monday of its week).
2. Duplicates are removed and the keys are sorted.
3. `functools.reduce` splits the keys into runs of consecutive periods.
4. The longest run is the **longest streak**. The last run is the **current streak** if it ends in the current or the previous period; otherwise the current streak is 0.
5. The **completion rate** is completed periods divided by all periods since the habit was created.

## Tests
```bash
python -m pytest
```
27 unit tests cover the Habit class (including week borders), streak and rate calculations, the SQLite repository (using a temporary in-memory database), the manager's validation, the sample data and the CLI (with scripted keyboard input).

## Project structure
```
oofpp_habits_project/
├── main.py                    starts the application
├── README.md                  this documentation
├── requirements.txt           pytest (tests only)
├── habit_tracker/
│   ├── habit.py               Habit class, Periodicity enum, period helpers
│   ├── repository.py          SQLite storage (HabitRepository)
│   ├── manager.py             application logic and validation (HabitManager)
│   ├── analytics.py           pure functions for streaks and statistics
│   ├── cli.py                 menu and screens
│   └── sample_data.py         example habits
└── tests/                     pytest unit tests
```

## Design
The application is split into layers, each with one job:

`CLI  ->  HabitManager  ->  HabitRepository  ->  SQLite (habits.db)`

- The **CLI** only reads input and prints output; it never touches the database.
- The **HabitManager** applies the rules (unique names, one completion per period) and raises `HabitError` with a clear message.
- The **HabitRepository** converts between database rows and `Habit` objects.
- The **analytics** module contains only pure functions (no printing, no saving, no changes), written in functional style with `map`, `filter` and `reduce`.

### Database
| Table | Columns |
|---|---|
| `habit` | `id`, `name` (unique, not case-sensitive), `description`, `periodicity` (daily/weekly), `created_at` |
| `completion` | `id`, `habit_id` (foreign key, `ON DELETE CASCADE`), `completed_at` |

Timestamps are stored as ISO-8601 text.

## Limitations and ideas for the future
- Single user, local file only
- Periods are daily and weekly; a monthly period could be added in `Periodicity` and `period_start`
- A reminder for open habits, or a web or graphical front end on top of `HabitManager`
