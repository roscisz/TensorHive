import pytest

from datetime import datetime, timedelta
from tensorhive.models.Restriction import Restriction


def test_restriction_creation(tables):
    starts_at = datetime.utcnow() + timedelta(minutes=5)
    duration = timedelta(hours=12)
    new_restriction = Restriction(name='TestRestriction', starts_at=starts_at,
                                  ends_at=starts_at + duration, is_global=False)
    new_restriction.save()

    assert new_restriction.id is not None


def test_get_global_restrictions_returns_them(tables):
    starts_at = datetime.utcnow() + timedelta(minutes=5)
    duration = timedelta(hours=12)
    new_restriction = Restriction(name='TestRestriction', starts_at=starts_at,
                                  ends_at=starts_at + duration, is_global=True)
    new_restriction.save()

    assert new_restriction in Restriction.get_global_restrictions()


def test_apply_restriction_to_user(tables, restriction, new_user):
    new_user.save()
    restriction.apply_to_user(new_user)

    assert restriction in new_user.get_restrictions()
    assert new_user in restriction.users


def test_apply_restriction_to_group(tables, restriction, new_group):
    restriction.apply_to_group(new_group)

    assert restriction in new_group.get_restrictions()
    assert new_group in restriction.groups


def test_group_restrictions_apply_to_its_members(tables, restriction, new_group_with_member):
    restriction.apply_to_group(new_group_with_member)

    assert restriction in new_group_with_member.get_restrictions()
    assert restriction in new_group_with_member.users[0].get_restrictions(include_group=True)
    assert new_group_with_member in restriction.groups


def test_it_should_be_impossible_to_create_restriction_with_end_time_happening_before_start_time(tables):
    start_time = datetime.utcnow() + timedelta(hours=5)
    end_time = datetime.utcnow() + timedelta(minutes=1)
    restriction = Restriction(name='Test', starts_at=start_time, ends_at=end_time, is_global=False)

    with pytest.raises(AssertionError):
        restriction.save()


def test_it_should_be_impossible_to_create_or_edit_restriction_that_already_expired(tables):
    start_time = datetime.utcnow() - timedelta(hours=5)
    end_time = start_time + timedelta(hours=1)
    restriction = Restriction(name='Test', starts_at=start_time, ends_at=end_time, is_global=False)

    with pytest.raises(AssertionError):
        restriction.save()


def test_apply_restriction_to_resource(tables, restriction, resource1):
    restriction.apply_to_resource(resource1)

    assert restriction in resource1.get_restrictions()
    assert resource1 in restriction.resources


def test_global_restriction_applies_to_all_resources(tables, restriction, resource1, resource2):
    restriction.is_global = True
    restriction.save()

    assert len(restriction.resources) == 0
    assert restriction in resource1.get_restrictions(include_global=True)
    assert restriction in resource2.get_restrictions(include_global=True)


def test_restriction_without_schedules_is_active_only_when_between_start_and_end_dates(tables):
    start_time = datetime.utcnow() - timedelta(hours=5)
    end_time = datetime.utcnow() + timedelta(hours=5)
    active_restriction = Restriction(name='ActiveRestriction', starts_at=start_time, ends_at=end_time, is_global=False)
    active_restriction.save()

    start_time = datetime.utcnow() + timedelta(hours=1)
    inactive_restriction = Restriction(name='InactiveRestriction', starts_at=start_time, ends_at=end_time,
                                       is_global=False)
    inactive_restriction.save()

    assert active_restriction.is_active is True
    assert inactive_restriction.is_active is False


def test_restriction_with_schedules_is_active_only_when_at_least_one_of_its_schedules_is_active(tables,
                                                                                                active_schedule,
                                                                                                inactive_schedule):
    start_time = datetime.utcnow() - timedelta(hours=5)
    end_time = datetime.utcnow() + timedelta(hours=5)
    restriction = Restriction(name='ActiveRestriction', starts_at=start_time, ends_at=end_time, is_global=False)
    restriction.save()

    restriction.add_schedule(inactive_schedule)
    assert restriction.is_active is False

    print(active_schedule.is_active)
    restriction.add_schedule(active_schedule)
    assert restriction.is_active is True
