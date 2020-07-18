import pytest
import datetime
from tensorhive.models.Reservation import Reservation
from tensorhive.models.Restriction import Restriction
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from tensorhive.models.User import User
from tensorhive.models.Group import Group
from tensorhive.models.Resource import Resource
from tensorhive.models.Role import Role
from datetime import timedelta


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
    new_user.save()
    now = datetime.datetime.utcnow()
    duration = timedelta(minutes=60)

    return Reservation(
        user_id=new_user.id,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        protected_resource_id='0123456789012345678901234567890123456789',
        starts_at=now,
        ends_at=now + duration,
    )


@pytest.fixture(scope='function')
def new_reservation_2(new_user, new_admin):
    new_user.save()
    new_admin.save()
    now = datetime.datetime.utcnow()
    duration = timedelta(minutes=60)

    return Reservation(
        user_id=new_admin.id,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        protected_resource_id='0123456789012345678901234567890123456789',
        starts_at=now,
        ends_at=now + duration,
    )


@pytest.fixture(scope='function')
def new_group():
    return Group(name='TestGroup1')


@pytest.fixture(scope='function')
def new_group_with_member(new_user):
    group = Group(name='TestGroup1')
    group.save()
    group.add_user(new_user)
    return group


@pytest.fixture(scope='function')
def resource1():
    resource = Resource(id='34943e60-0acd-4c31-b96e-02f88cc156f3')
    resource.save()
    return resource


@pytest.fixture(scope='function')
def resource2():
    resource = Resource(id='d5c501b1-8fbc-4dc2-9153-5f06af785336', name='Custom name')
    resource.save()
    return resource


@pytest.fixture(scope='function')
def restriction():
    start_time = datetime.datetime.utcnow() + timedelta(minutes=5)
    end_time = start_time + timedelta(hours=8)
    restriction = Restriction(name='TestRestriction', starts_at=start_time, ends_at=end_time, is_global=False)
    restriction.save()
    return restriction


@pytest.fixture(scope='function')
def schedule():
    schedule_expression = '12345'
    start_time = datetime.time(8, 0, 0)
    end_time = datetime.time(10, 0, 0)
    schedule = RestrictionSchedule(schedule_days=schedule_expression, hour_start=start_time, hour_end=end_time)
    schedule.save()
    return schedule
