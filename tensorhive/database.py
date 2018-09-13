from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tensorhive.config import DB_CONFIG
engine = create_engine(DB_CONFIG.SQLALCHEMY_DATABASE_URI, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from tensorhive.models.user import UserModel
    from tensorhive.models.reservation_event import ReservationEventModel
    from tensorhive.models.auth import RevokedTokenModel
    return Base.metadata.create_all(bind=engine)
