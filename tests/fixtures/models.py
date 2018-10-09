import pytest
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from datetime import datetime, timedelta

@pytest.fixture(scope='module')
def new_user():
    return User(username='miczi', password='TEST PASSWORD')


@pytest.fixture(scope='module')
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