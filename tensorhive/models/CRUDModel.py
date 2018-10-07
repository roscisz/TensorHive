from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from tensorhive.database import db_session
import logging
log = logging.getLogger(__name__)


class CRUDModel:

    @classmethod
    def create(cls, **kw):
        new_object = cls(**kw)
        try:
            db_session.add(new_object)
            db_session.commit()
        # OperationalError
        except SQLAlchemyError as e:
            db_session.rollback()
            log.error('{cause} with {data}'.format(cause=e.__cause__, data=new_object))
            raise e
        else:
            log.debug('Created {}'.format(new_object))
            return new_object

    def destroy(self):
        try:
            db_session.delete(self)
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            log.error('{} with {}'.format(cause=e.__cause__, data=self))
            raise e
        else:
            log.debug('Deleted {}'.format(self))
            return self

    @classmethod
    def get(cls, id):
        try:
            result = cls.query.filter_by(id=id).one()
        except MultipleResultsFound as e:
            msg = 'There are multiple {} records with the same id={}!'.format(cls.__name__, id)
            log.error(msg)
            raise MultipleResultsFound(msg)
        except NoResultFound as e:
            msg = 'There is no record {} with id={}!'.format(cls.__name__, id)
            log.error(msg)
            raise NoResultFound(msg)
        else:
            return result
