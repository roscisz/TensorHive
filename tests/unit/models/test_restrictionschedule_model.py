import pytest
import datetime

from tensorhive.models.RestrictionSchedule import RestrictionSchedule


def test_schedule_creation(tables):
    schedule_expression = '12345'
    starts_at = datetime.time(8, 0, 0)
    ends_at = datetime.time(15, 0, 0)
    schedule = RestrictionSchedule(schedule_days=schedule_expression, hour_start=starts_at, hour_end=ends_at)
    schedule.save()


def test_cannot_create_schedule_with_wrong_schedule_expression(tables):
    starts_at = datetime.time(8, 0, 0)
    ends_at = datetime.time(15, 0, 0)
    wrong_schedule_expression = '1458'
    schedule = RestrictionSchedule(schedule_days=wrong_schedule_expression, hour_start=starts_at, hour_end=ends_at)
    with pytest.raises(AssertionError):
        schedule.save()

    schedule.schedule_days = '1123'
    with pytest.raises(AssertionError):
        schedule.save()


def test_add_schedule_to_restriction(tables, restriction, schedule):
    restriction.add_schedule(schedule)

    assert schedule in restriction.schedules
    assert restriction in schedule.restrictions
