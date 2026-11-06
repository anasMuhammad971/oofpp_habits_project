"""Habit Tracker: a command line application to create, complete and analyse habits.

Package layout (each module has exactly one job):

* ``habit``       - the domain model (``Habit`` class and ``Periodicity`` enum)
* ``repository``  - saving and loading habits with SQLite
* ``manager``     - application logic and input validation
* ``analytics``   - pure functions for streaks and statistics (functional style)
* ``cli``         - menu, user input and screen output
* ``sample_data`` - example habits for demonstration
"""
