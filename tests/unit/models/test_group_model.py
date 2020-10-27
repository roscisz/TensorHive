import pytest
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.Group import Group
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException


def test_group_creation(tables):
    new_group = Group(name='test').save()
    assert new_group.id is not None


def test_adding_user_to_a_group(tables, new_user, new_group):
    new_user.save()
    new_group.add_user(new_user)

    assert new_user in new_group.users
    assert new_group in new_user.groups


def test_removing_user_from_a_group(tables, new_group_with_member):
    user = new_group_with_member.users[0]
    new_group_with_member.remove_user(user)

    assert user not in new_group_with_member.users
    assert new_group_with_member not in user.groups


def test_removing_user_from_a_group_that_he_doesnt_belong_to_fails(tables, new_user, new_group):
    new_group.save()
    new_user.save()

    with pytest.raises(InvalidRequestException):
        new_group.remove_user(new_user)


def test_adding_user_to_a_group_that_he_is_already_in_fails(tables, new_group_with_member):
    user = new_group_with_member.users[0]

    with pytest.raises(InvalidRequestException):
        new_group_with_member.add_user(user)


def test_marking_group_as_a_default(tables, new_group):
    new_group.is_default = True
    new_group.save()

    assert Group.get(new_group.id).is_default
    assert new_group in Group.get_default_groups()


def test_get_default_group(tables, new_group):
    new_group.is_default = True
    new_group.save()

    assert new_group in Group.get_default_groups()


def test_get_default_without_default_group(tables, new_group):
    new_group.save()

    assert len(Group.get_default_groups()) == 0


def test_more_than_one_default_group(tables, new_group):
    new_group.is_default = True
    new_group.save()

    another_group = Group(name='AnotherGroup')
    another_group.is_default = True
    another_group.save()

    defaults = Group.get_default_groups()
    assert new_group in defaults
    assert another_group in defaults
