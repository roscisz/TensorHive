import pytest


@pytest.yield_fixture(scope='function')
def tables():
    from tensorhive.database import Base, engine
    from tensorhive.models.User import User
    from tensorhive.models.Group import Group, User2Group
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.Resource import Resource
    from tensorhive.models.Restriction import Restriction, Restriction2Assignee, Restriction2Resource
    from tensorhive.models.RestrictionSchedule import RestrictionSchedule
    from tensorhive.models.Role import Role
    from tensorhive.models.RevokedToken import RevokedToken
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
