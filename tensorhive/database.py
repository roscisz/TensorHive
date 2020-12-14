from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from tensorhive.config import DB, CONFIG_FILES
from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
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


def _import_models() -> None:
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


def initialize_db(alembic_config) -> None:
    log.info('[•] Initializing DB...')
    Base.metadata.create_all(bind=engine, checkfirst=True)
    command.stamp(alembic_config, 'head')
    log.info('[✔] DB created ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))


def _schema_version_is_current(alembic_config, connection):
    log.info('[•] Checking version of DB: ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
    migration_ctx = MigrationContext.configure(connection)
    alembic_config.attributes['connection'] = connection
    script_directory = ScriptDirectory.from_config(alembic_config)
    current_revision = migration_ctx.get_current_revision()
    if current_revision is None:
        log.error('[✘] DB has not been stamped. This makes automatic migration impossible. If you have been using TH'
                  '< 0.3.4, use alembic to upgrade the DB, otherwise please report a bug. Now using the DB as is...')
        return True
    else:
        return current_revision == script_directory.get_current_head()


def _upgrade_db_schema(alembic_config):
    command.upgrade(alembic_config, 'head')
    log.info('[✔] Database upgraded')


def ensure_db_with_current_schema() -> None:
    """Makes sure that there is a DB in proper version and creates or upgrades the DB if needed"""
    _import_models()

    alembic_config = Config(CONFIG_FILES.ALEMBIC_CONFIG_PATH)
    alembic_config.set_main_option("script_location", CONFIG_FILES.MIGRATIONS_CONFIG_PATH)

    if not check_if_db_exists():
        initialize_db(alembic_config)
    else:
        with engine.begin() as connection:
            if _schema_version_is_current(alembic_config, connection):
                log.info('[✔] DB up to date')
            else:
                log.warning('[•] DB schema is out of date, trying to upgrade automatically')
                _upgrade_db_schema(alembic_config)


def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')


event.listen(engine, 'connect', _fk_pragma_on_connect)
