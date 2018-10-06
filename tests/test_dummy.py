from tensorhive.models.RevokedToken import RevokedToken
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import pytest


@pytest.fixture(scope='session')
def engine():
    return create_engine('sqlite:////home/miczi/.config/TensorHive/database.sqlite')


@pytest.yield_fixture(scope='session')
def tables(engine):
    RevokedToken.metadata.create_all(engine)
    yield
    RevokedToken.metadata.drop_all(engine)


@pytest.yield_fixture
def dbsession(engine, tables):
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


@pytest.mark.parametrize("original_jti,expected_jti", [
    ("qwe", "qwe"),
    ("asd", "asd"),
    ("zxc", "wrong"),
])
def test_ehlo(dbsession, original_jti, expected_jti):
    t = RevokedToken(id=1, jti=original_jti)
    dbsession.add(t)
    dbsession.commit()
    assert t.jti == expected_jti