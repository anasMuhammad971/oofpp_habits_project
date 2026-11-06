from datetime import datetime, timedelta

from habit_tracker import analytics
from habit_tracker.habit import Habit, Periodicity

TODAY = datetime(2026, 3, 18, 12)   # a Wednesday


def daily(days_ago, created_days_ago=30):
    created = TODAY - timedelta(days=created_days_ago)
    return Habit("d", periodicity=Periodicity.DAILY, created_at=created,
                 completions=[TODAY - timedelta(days=d) for d in days_ago])


def weekly(weeks_ago, created_weeks_ago=6):
    created = TODAY - timedelta(weeks=created_weeks_ago)
    return Habit("w", periodicity=Periodicity.WEEKLY, created_at=created,
                 completions=[TODAY - timedelta(weeks=w) for w in weeks_ago])


def test_no_completions():
    h = daily([])
    assert analytics.longest_streak(h) == 0
    assert analytics.current_streak(h, TODAY) == 0


def test_longest_streak_with_gap():
    h = daily([0, 1, 2, 5, 6, 7, 8, 9])        # 3 days, gap, 5 days
    assert analytics.longest_streak(h) == 5
    assert analytics.current_streak(h, TODAY) == 3


def test_current_streak_alive_if_done_yesterday():
    assert analytics.current_streak(daily([1, 2, 3]), TODAY) == 3


def test_current_streak_broken_after_two_missed_days():
    assert analytics.current_streak(daily([2, 3, 4]), TODAY) == 0


def test_weekly_streak_across_week_borders():
    h = weekly([0, 1, 2, 4])
    assert analytics.longest_streak(h) == 3
    assert analytics.current_streak(h, TODAY) == 3


def test_completion_rate():
    h = daily(list(range(0, 10)), created_days_ago=9)   # 10 days, all done
    assert analytics.completion_rate(h, TODAY) == 1.0
    h = daily([0, 2, 4, 6, 8], created_days_ago=9)
    assert analytics.completion_rate(h, TODAY) == 0.5


def test_filter_and_best_overall():
    habits = [daily([0, 1, 2]), weekly([0, 1, 2, 3, 4])]
    assert len(analytics.filter_by_periodicity(habits, Periodicity.WEEKLY)) == 1
    best, streak = analytics.longest_streak_all(habits)
    assert best.periodicity is Periodicity.WEEKLY and streak == 5
    assert analytics.longest_streak_all([]) is None


def test_analytics_do_not_change_the_habit():
    h = daily([0, 1, 2])
    before = list(h.completions)
    analytics.summarise([h], TODAY)
    assert h.completions == before
