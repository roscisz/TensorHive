import pytest


@pytest.yield_fixture(scope='function')
def tables():
    from tensorhive.database import Base, engine
    from tensorhive.models.User import User
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.Role import Role
    from tensorhive.models.RevokedToken import RevokedToken
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
