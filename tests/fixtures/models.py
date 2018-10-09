import pytest
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from tensorhive.models.Role import Role
from datetime import datetime, timedelta

@pytest.fixture(scope='function')
def admin_role():
    return Role(name='admin')

@pytest.fixture(scope='function')
def user_role():
    return Role(name='user')

@pytest.fixture(scope='function')
def new_user(user_role):
    return User(username='administrantee', password='TEST PASSWORD', roles=[user_role])

@pytest.fixture(scope='function')
def new_admin(admin_role, user_role):
    return User(username='justuser', password='TEST PASSWORD', roles=[admin_role, user_role])

@pytest.fixture(scope='function')
def new_reservation(new_user):
    now = datetime.utcnow()
    duration = timedelta(minutes=30)

    return Reservation(
        user=new_user,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        protected_resource_id='TEST_UUID',
        starts_at=now,
        ends_at=now + duration,
    )