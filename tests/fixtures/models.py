import pytest
import datetime
from tensorhive.models.Reservation import Reservation
from tensorhive.models.Restriction import Restriction
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from tensorhive.models.User import User
from tensorhive.models.Group import Group
from tensorhive.models.Resource import Resource
from tensorhive.models.Role import Role
from tensorhive.models.Job import Job, JobStatus
from tensorhive.models.Task import Task, TaskStatus
from tensorhive.models.CommandSegment import CommandSegment, SegmentType
from datetime import timedelta


@pytest.fixture(scope='function')
def new_user():
    return User(username='administrantee',
                password='TEST PASSWORD',
                roles=[Role(name='user')])


@pytest.fixture(scope='function')
def new_user_2():
    return User(username='AnotherUser',
                password='TEST PASSWORD',
                roles=[Role(name='user')])


@pytest.fixture(scope='function')
def new_admin():
    return User(username='justuser',
                password='TEST PASSWORD',
                roles=[Role(name='user'), Role(name='admin')])


@pytest.fixture(scope='function')
def new_reservation(new_user, resource1):
    new_user.save()
    now = datetime.datetime.utcnow()
    duration = timedelta(minutes=60)

    return Reservation(
        user_id=new_user.id,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        resource_id=resource1.id,
        start=now,
        end=now + duration,
    )


@pytest.fixture(scope='function')
def new_reservation_2(new_user, new_admin, resource1):
    new_user.save()
    new_admin.save()
    now = datetime.datetime.utcnow()
    duration = timedelta(minutes=60)

    return Reservation(
        user_id=new_admin.id,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        resource_id=resource1.id,
        start=now,
        end=now + duration,
    )


@pytest.fixture(scope='function')
def past_reservation(new_user, resource1):
    new_user.save()
    start = datetime.datetime.utcnow() - timedelta(hours=5)
    duration = timedelta(minutes=60)

    return Reservation(
        user_id=new_user.id,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        resource_id=resource1.id,
        start=start,
        end=start + duration,
    )


@pytest.fixture(scope='function')
def active_reservation(new_user, resource1):
    new_user.save()
    start = datetime.datetime.utcnow() - timedelta(hours=5)
    duration = timedelta(hours=10)

    return Reservation(
        user_id=new_user.id,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        resource_id=resource1.id,
        start=start,
        end=start + duration,
    )


@pytest.fixture(scope='function')
def future_reservation(new_user, resource1):
    new_user.save()
    start = datetime.datetime.utcnow() + timedelta(hours=5)
    duration = timedelta(hours=10)

    return Reservation(
        user_id=new_user.id,
        title='TEST TITLE',
        description='TEST_DESCRIPTION',
        resource_id=resource1.id,
        start=start,
        end=start + duration,
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
    resource = Resource(id='GPU-d38d4de3-85ee-e837-3d87-e8e2faeb6a63')

    resource.save()
    return resource


@pytest.fixture(scope='function')
def resource2():
    resource = Resource(id='GPU-d38d4de3-85ee-e837-3d87-e8e2faeb6a64', name='Custom name')
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
def permissive_restriction(new_user):
    start_time = datetime.datetime.utcnow() - timedelta(days=10)
    end_time = None
    restriction = Restriction(name='PermissiveRestriction', starts_at=start_time, ends_at=end_time, is_global=True)
    restriction.apply_to_user(new_user)
    restriction.save()
    return restriction


@pytest.fixture(scope='function')
def active_schedule():
    schedule_expression = '1234567'
    start_time = datetime.time(0, 0, 0)
    end_time = datetime.time(23, 59, 59)
    schedule = RestrictionSchedule(schedule_days=schedule_expression, hour_start=start_time, hour_end=end_time)
    schedule.save()
    return schedule


@pytest.fixture(scope='function')
def inactive_schedule():
    today = str(datetime.datetime.utcnow().weekday() + 1)
    schedule_expression = '1234567'.replace(today, '')
    start_time = datetime.time(8, 0, 0)
    end_time = datetime.time(10, 0, 0)
    schedule = RestrictionSchedule(schedule_days=schedule_expression, hour_start=start_time, hour_end=end_time)
    schedule.save()
    return schedule


@pytest.fixture(scope='function')
def new_job(new_user):
    new_user.save()
    job = Job(name='job_name',
              description='testDescription',
              user_id=1,
              status=JobStatus.not_running)
    job.save()
    return job


@pytest.fixture(scope='function')
def new_job_with_task(new_user, new_task):
    new_user.save()
    job = Job(name='job_name',
              description='testDescription',
              user_id=1,
              status=JobStatus.not_running)
    job.save()
    job.add_task(new_task)
    return job


@pytest.fixture(scope='function')
def new_task():
    task = Task(command='python command.py',
                hostname='localhost',
                status=TaskStatus.not_running)
    cmd_segment = CommandSegment(
        name='--batch_size',
        _segment_type=SegmentType.parameter
    )
    task.add_cmd_segment(cmd_segment, '32')
    task.save()
    return task


@pytest.fixture(scope='function')
def new_task_2():
    task = Task(command='python command2.py',
                hostname='remotehost',
                status=TaskStatus.not_running)
    cmd_segment = CommandSegment(
        name='--rank',
        _segment_type=SegmentType.parameter
    )
    task.add_cmd_segment(cmd_segment, '1')
    task.save()
    return task
