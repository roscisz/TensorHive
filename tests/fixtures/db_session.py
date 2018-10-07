import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


@pytest.fixture(scope='session')
def engine():
    return create_engine('sqlite:////home/miczi/.config/TensorHive/database.sqlite')


@pytest.yield_fixture(scope='session')
def tables(engine):
    from tensorhive.models.RevokedToken import RevokedToken
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.Role import Role
    from tensorhive.models.User import User

    engine = create_engine('sqlite:////home/miczi/.config/TensorHive/database.sqlite',
                       convert_unicode=True,
                       echo=False)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                            autoflush=False,
                                            bind=engine))
    Base = declarative_base()
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine, checkfirst=True)

    # Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.yield_fixture
def db_session(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()