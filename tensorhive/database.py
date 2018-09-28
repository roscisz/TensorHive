from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from tensorhive.config import DB
from tensorhive.controllers.user.CreateUserController import CreateUserController
from tensorhive.models.role.RoleModel import RoleModel
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
    
    if database_exists(DB.SQLALCHEMY_DATABASE_URI):
        log.info('[•] Database found ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
        new_user = UserModel(
            username=user['username'],
            password=UserModel.generate_hash(user['password'])
        )
        new_role = RoleModel(
            name='user',
            user_id=new_user.id
        )

        try:
            new_user.save_to_db()
        except:
            log.error('[•] Admin is not created.')
        new_role = RoleModel(
            name='user',
            user_id=new_user.id
        )
        log.info('[•] Admin created found ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
    else:
        # Double check via checkfirst=True (does not execute CREATE query on tables which already exist)
        Base.metadata.create_all(bind=engine, checkfirst=True)
        log.info('[✔] Database created ({path})'.format(path=DB.SQLALCHEMY_DATABASE_URI))
