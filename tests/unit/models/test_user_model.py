import pytest
from sqlalchemy.exc import OperationalError, IntegrityError
from tensorhive.models.User import User


# @pytest.mark.parametrize('test_username', [
#     'foobar',
#     '_____',
#     'zzzzz',
# ])
@pytest.mark.usefixtures('db_session')
def test_exception_on_creating_user_with_no_password(db_session):
    with pytest.raises(IntegrityError):
        new_user = User(username='foo')

        db_session.add(new_user)
        db_session.commit()

@pytest.mark.usefixtures('db_session')
def test_exception_on_creating_user_with_not_unique_username(db_session):
    with pytest.raises(IntegrityError):
        duplicated_username = 'foo'
        password = 'irrelevant_password'

        existing_user = User(username=duplicated_username, password=password)
        duplicated_user = User(username=duplicated_username, password=password)

        db_session.add(existing_user)
        db_session.add(duplicated_user)
        db_session.commit()
