import pytest
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from tensorhive.models.Role import Role
from tensorhive.models.Job import Job
from tensorhive.models.Task import Task
from datetime import datetime, timedelta


@pytest.fixture(scope='function')
def new_user():
    return User(username='administrantee',
                password='TEST PASSWORD',
                roles=[Role(name='user')])


@pytest.fixture(scope='function')
def new_admin():
    return User(username='justuser',
                password='TEST PASSWORD',
                roles=[Role(name='user'), Role(name='admin')])


@pytest.fixture(scope='function')
def new_reservation(new_user):
    now = datetime.utcnow()
    duration = timedelta(minutes=60)

    return Reservation(
        user_id=1,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        protected_resource_id='0123456789012345678901234567890123456789',
        starts_at=now,
        ends_at=now + duration,
    )


@pytest.fixture(scope='function')
def new_reservation_2(new_user):
    now = datetime.utcnow()
    duration = timedelta(minutes=60)

    return Reservation(
        user_id=2,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        protected_resource_id='0123456789012345678901234567890123456789',
        starts_at=now,
        ends_at=now + duration,
    )


@pytest.fixture(scope='function')
def new_job():
    return Job(name='job_name',
                description='testDescription',
                user_id=1)

@pytest.fixture(scope='function')
def new_task():
    return Task(command='python command.py --batch_size 32',
                host='hostname')
#                user_id=1)