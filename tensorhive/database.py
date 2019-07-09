from sqlalchemy import create_engine
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


def init_db() -> None:
    '''Creates the database, tables (if they does not exist)'''
    # Import all modules that define models so that
    # they could be registered properly on the metadata.
    from tensorhive.models.User import User
    from tensorhive.models.Reservation import Reservation
    from tensorhive.models.RevokedToken import RevokedToken
    from tensorhive.models.Role import Role
    from tensorhive.models.Task import Task

    if not database_exists(DB.SQLALCHEMY_DATABASE_URI):
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info('[✔] Database created ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
    else:
        log.info('[•] Database found ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
