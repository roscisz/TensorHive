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