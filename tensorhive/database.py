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
    from tensorhive.models.user import UserModel
    from tensorhive.models.reservation_event import ReservationEventModel
    from tensorhive.models.auth import RevokedTokenModel
    from tensorhive.models.role import RoleModel
    from tensorhive.models.user.UserModel import UserModel

    if database_exists(DB.SQLALCHEMY_DATABASE_URI):
        if not UserModel.find_by_username('admin'):
            log.info('[•] Admin has not been found.')
            create_admin()
        log.info('[•] Database found ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))

    else:
        # Double check via checkfirst=True (does not execute CREATE query on tables which already exist)
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info('[✔] Database created ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
        create_admin()

def create_admin():
    from tensorhive.models.user.UserModel import UserModel
    from tensorhive.models.role.RoleModel import RoleModel
    admin_default_password  = 'tensorhive_admin'
    new_user = UserModel(
        username='admin',
        password=UserModel.generate_hash(admin_default_password)
    )

    try:
        new_user.save_to_db()
        for role_name in ['user', 'admin']:
            new_role = RoleModel(
                name=role_name,
                user_id=new_user.id
            )
            try:
                new_role.save_to_db()
            except:
                log.error('[•] Admin is not created due to role exception.')
    except:
        log.error('[•] Admin is not created.')

    log.info('[•] Admin created. Login: {name} . Password : {password} .'.format(name=new_user.username, password=admin_default_password))