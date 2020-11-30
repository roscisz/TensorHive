from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from tensorhive.config import DB
import logging
import os
log = logging.getLogger(__name__)

if bool(os.environ.get('PYTEST')):
    db_uri = DB.TEST_DATABASE_URI
else:
    db_uri = DB.SQLALCHEMY_DATABASE_URI

engine = create_engine(db_uri, convert_unicode=True, echo=False)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def check_if_db_exists() -> bool:
    return database_exists(DB.SQLALCHEMY_DATABASE_URI)


def init_db_schema_if_nonexistent() -> None:
    """Creates the database, tables (if they does not exist)"""
    # Import all modules that define models so that
    # they could be registered properly on the metadata.
    from tensorhive.models.User import User
    from tensorhive.models.Group import Group, User2Group
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.Resource import Resource
    from tensorhive.models.Restriction import Restriction, Restriction2Assignee, Restriction2Resource
    from tensorhive.models.RestrictionSchedule import RestrictionSchedule, Restriction2Schedule
    from tensorhive.models.RevokedToken import RevokedToken
    from tensorhive.models.Role import Role
    from tensorhive.models.Task import Task

    if not check_if_db_exists():
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info('[✔] Database created ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
    else:
        log.info('[•] Database found ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


event.listen(engine, 'connect', _fk_pragma_on_connect)
