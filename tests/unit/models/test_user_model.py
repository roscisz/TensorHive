import pytest
from sqlalchemy.exc import IntegrityError
from tensorhive.models.User import User


def test_user_creation(tables, new_user, new_admin):
    new_user.save()
    assert set(new_user.role_names) == set(['user'])
    assert new_user.id

    new_admin.save()
    assert new_admin.id
    assert set(new_admin.role_names) == set(['admin', 'user'])


# TODO May want to use faker fixture everywhere
@pytest.mark.parametrize('test_name, test_username', [
    ('too_short', 'a'),
    ('too_long', 'a' * 31),
    ('empty', ''),
    ('sneaky', '         '),
    ('special', '!@#$%^&*()[]{};<>?/'),
    ('blacklisted', 'nonurlfriendly!!!'),
    ('blacklisted', 'jerk'),
])
def test_exception_on_creating_user_with_invalid_username(tables, test_name, test_username):
    with pytest.raises(AssertionError):
        User(username=test_username, password='irrelevent_password').save()


def test_exception_on_creating_user_with_no_password(tables):
    with pytest.raises(IntegrityError):
        User(username='valid_username').save()


def test_exception_on_creating_user_with_not_unique_username(tables):
    with pytest.raises(IntegrityError):
        duplicated_username = 'valid_username'
        password = 'irrelevant_password'

        existing_user = User(username=duplicated_username, password=password)
        duplicated_user = User(username=duplicated_username, password=password)

        existing_user.save()
        duplicated_user.save()
