import pytest
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from tensorhive.models.User import User


@pytest.mark.parametrize('test_username', [
    'foobar',
    '_____',
    'zzzzz',
])
@pytest.mark.usefixtures('db_session')
def test_create(db_session, test_username):
    #print(test_username)
    user = User.create(username=test_username, password='random')
    assert user
