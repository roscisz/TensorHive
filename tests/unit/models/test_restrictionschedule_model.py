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


def test_add_schedule_to_restriction(tables, restriction, active_schedule):
    restriction.add_schedule(active_schedule)

    assert active_schedule in restriction.schedules
    assert restriction in active_schedule.restrictions


def test_schedule_is_active_method_returns_valid_status(tables, restriction):
    # schedule that runs only on current day of the week
    today_schedule_expression = str(datetime.datetime.utcnow().weekday() + 1)
    hour_start = datetime.time(0, 0, 0)
    hour_end = datetime.time(23, 59, 59)
    active_schedule = RestrictionSchedule(schedule_days=today_schedule_expression, hour_start=hour_start,
                                          hour_end=hour_end)
    active_schedule.save()

    # schedule that runs on every day of the week except for today
    not_today_schedule_expression = '1234567'.replace(today_schedule_expression, '')
    inactive_schedule = RestrictionSchedule(schedule_days=not_today_schedule_expression, hour_start=hour_start,
                                            hour_end=hour_end)
    inactive_schedule.save()

    assert active_schedule.is_active is True
    assert inactive_schedule.is_active is False
