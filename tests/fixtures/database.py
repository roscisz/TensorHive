import pytest


@pytest.fixture(scope='function')
def tables():
    from tensorhive.database import Base, engine, db_session
    from tensorhive.models.User import User
    from tensorhive.models.Group import Group, User2Group
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.Resource import Resource
    from tensorhive.models.Restriction import Restriction, Restriction2Assignee, Restriction2Resource
    from tensorhive.models.RestrictionSchedule import RestrictionSchedule
    from tensorhive.models.Role import Role
    from tensorhive.models.RevokedToken import RevokedToken
    from tensorhive.models.Job import Job
    from tensorhive.models.Task import Task
    from tensorhive.models.CommandSegment import CommandSegment2Task, CommandSegment
    Base.metadata.create_all(engine)
    db_session.remove()  # that makes sure we won't be holding on to any cached entities between test cases
    yield
    Base.metadata.drop_all(engine)
