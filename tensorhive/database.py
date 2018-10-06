from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from tensorhive.config import DB

import logging
log = logging.getLogger(__name__)

engine = create_engine(DB.SQLALCHEMY_DATABASE_URI,
                       convert_unicode=True,
                       echo=False)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db() -> None:
    '''Creates the database, tables (if they does not exist)'''
    # Import all modules that define models so that
    # they could be registered properly on the metadata.
    from tensorhive.models.User import User
    from tensorhive.models.reservation_event import ReservationEventModel
    from tensorhive.models.auth import RevokedTokenModel
    from tensorhive.models.role import RoleModel
    

    if database_exists(DB.SQLALCHEMY_DATABASE_URI):
        if database_has_no_users():
            log.info('[•] Admin has not been found.')
            create_admin()
        log.info('[•] Database found ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))

    else:
        # Double check via checkfirst=True (does not execute CREATE query on tables which already exist)
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info('[✔] Database created ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
        create_admin()

def create_admin():
    import click
    from tensorhive.models.user.UserModel import UserModel
    from tensorhive.models.role.RoleModel import RoleModel
    from sqlalchemy.orm.exc import NoResultFound

    try:
        UserModel.query.one()
    except NoResultFound:
        # User table is empty
        # TODO Add color output
        if click.confirm('''Database has no users. Would you like to create Administrator account now?''', abort=False):
            username = click.prompt('username', type=str)
            password = click.prompt('password', type=str, hide_input=True)

            new_user = UserModel(username=username, password=UserModel.generate_hash(password))
            new_user.save_to_db()

            # TODO Refactor roles, use only one role: admin (redundancy)
            admin_role = RoleModel(name='admin', user_id=new_user.id)
            user_role = RoleModel(name='user', user_id=new_user.id)

            admin_role.save_to_db()
            user_role.save_to_db()

            # TODO Handle failures
            click.echo('Account created successfully! Resuming...')