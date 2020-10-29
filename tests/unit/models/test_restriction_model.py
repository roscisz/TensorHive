import pytest

from datetime import datetime, timedelta
from tensorhive.models.Restriction import Restriction
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException


def test_restriction_creation(tables):
    starts_at = datetime.utcnow() + timedelta(minutes=5)
    duration = timedelta(hours=12)
    new_restriction = Restriction(name='TestRestriction', starts_at=starts_at,
                                  ends_at=starts_at + duration, is_global=False)
    new_restriction.save()

    assert new_restriction.id is not None


def test_indefinite_restriction_creation(tables):
    starts_at = datetime.utcnow() + timedelta(minutes=5)
    new_restriction = Restriction(name='TestRestriction', starts_at=starts_at, is_global=False)
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

    assert restriction in resource1.get_restrictions(include_global=False)
    assert resource1 in restriction.resources


def test_global_restriction_applies_to_all_resources(tables, restriction, resource1, resource2):
    restriction.is_global = True
    restriction.save()

    assert len(restriction.resources) == 0
    assert restriction in resource1.get_restrictions()
    assert restriction in resource2.get_restrictions()


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

    restriction.add_schedule(active_schedule)
    assert restriction.is_active is True


def test_restriction_with_dates_passed_as_string_gets_added_successfully(tables):
    new_restriction = Restriction(
        name='TestRestriction',
        is_global=False
    )
    new_restriction.starts_at = '2020-09-29T18:07:44.191Z'
    new_restriction.ends_at = '2120-09-30T18:07:44.191Z'
    new_restriction.save()


def test_when_trying_to_apply_restriction_to_the_same_group_twice_an_exception_is_thrown(tables, restriction,
                                                                                         new_group):
    new_group.save()
    restriction.apply_to_group(new_group)

    with pytest.raises(InvalidRequestException):
        restriction.apply_to_group(new_group)


def test_when_trying_to_apply_restriction_to_the_same_user_twice_an_exception_is_thrown(tables, restriction,
                                                                                        new_user):
    new_user.save()
    restriction.apply_to_user(new_user)

    with pytest.raises(InvalidRequestException):
        restriction.apply_to_user(new_user)


def test_when_trying_to_add_an_already_assigned_schedule_to_restriction_an_exception_is_thrown(tables, restriction,
                                                                                               inactive_schedule):
    inactive_schedule.save()
    restriction.add_schedule(inactive_schedule)

    with pytest.raises(InvalidRequestException):
        restriction.add_schedule(inactive_schedule)


def test_when_trying_to_add_an_already_assigned_resource_to_restriction_an_exception_is_thrown(tables, restriction,
                                                                                               resource1):
    resource1.save()
    restriction.apply_to_resource(resource1)

    with pytest.raises(InvalidRequestException):
        restriction.apply_to_resource(resource1)


def test_when_trying_to_remove_restriction_from_group_that_wasnt_assigned_to_it_an_exception_is_thrown(tables,
                                                                                                       restriction,
                                                                                                       new_group):
    new_group.save()

    with pytest.raises(InvalidRequestException):
        restriction.remove_from_group(new_group)


def test_when_trying_to_remove_restriction_from_user_that_wasnt_assigned_to_it_an_exception_is_thrown(tables,
                                                                                                      restriction,
                                                                                                      new_user):
    new_user.save()

    with pytest.raises(InvalidRequestException):
        restriction.remove_from_user(new_user)


def test_when_trying_to_remove_schedule_that_wasnt_assigned_to_restriction_an_exception_is_thrown(tables,
                                                                                                  restriction,
                                                                                                  inactive_schedule):
    inactive_schedule.save()

    with pytest.raises(InvalidRequestException):
        restriction.remove_schedule(inactive_schedule)


def test_when_trying_to_remove_restriction_from_resource_that_wasnt_assigned_to_it_an_exception_is_thrown(tables,
                                                                                                          restriction,
                                                                                                          resource1):
    resource1.save()

    with pytest.raises(InvalidRequestException):
        restriction.remove_from_resource(resource1)


def test_get_all_affected_users_will_return_all_users_affected_by_given_restriction(tables, restriction, new_user_2,
                                                                                    new_group_with_member):
    new_group_with_member.save()
    restriction.apply_to_group(new_group_with_member)

    new_user_2.save()
    restriction.apply_to_user(new_user_2)

    assert new_user_2 in restriction.users
    assert new_group_with_member.users[0] not in restriction.users

    all_affected_users = restriction.get_all_affected_users()
    assert new_user_2 in all_affected_users
    assert new_group_with_member.users[0] in all_affected_users
