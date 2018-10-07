import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URI = 'sqlite:///test_database.sqlite'


@pytest.fixture(scope='session')
def engine():
    return create_engine(SQLALCHEMY_DATABASE_URI)


@pytest.yield_fixture(scope='session')
def tables(engine):
    # Here you must define import all models
    # (required for setting up relationships and creating db schema)
    from tensorhive.database import Base
    from tensorhive.models.RevokedToken import RevokedToken
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.Role import Role
    from tensorhive.models.User import User

    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.yield_fixture
def db_session(engine, tables):
    '''Returns an sqlalchemy session, and after the test tears down everything properly.'''
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
@pytest.mark.usefixtures('db_session')
def valid_user(db_session):
    from tensorhive.models.User import User
    user = User(username='foobar', password='irrelevent_password')
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
@pytest.mark.usefixtures('db_session')
def valid_reservation(db_session, valid_user):
    from tensorhive.models.Reservation import Reservation
    import datetime
    starts_at = datetime.datetime.now()
    duration = datetime.timedelta(minutes=30)

    reservation = Reservation(
        start=starts_at,
        end=starts_at + duration,
        title='asd',
        description='',
        resource_id='UUID',
        user_id=valid_user.id
    )
    db_session.add(reservation)
    db_session.commit()
    return reservation