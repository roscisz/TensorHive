from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from tensorhive.database import db_session, Base
import logging
log = logging.getLogger(__name__)


class CRUDModel:
    def check_assertions(self):
        '''
        Purpose of this method is to run all necessary validation
        before saving model instance to database.

        Validation methods should raise AssertionError on failure
        '''
        raise NotImplementedError('Subclass must override this method!')

    def save(self):
        try:
            self.check_assertions()
            db_session.add(self)
            db_session.commit()
        except SQLAlchemyError as e:
            db_session.rollback()
            log.error('{cause} with {data}'.format(cause=e.__cause__, data=self))
            raise
        except AssertionError as e:
            log.error(e)
            raise
        except Exception as e:
            log.critical(type(e))
            raise
        else:
            log.debug('Saved {}'.format(self))
            return self

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
            result = db_session.query(cls).filter_by(id=id).one()
        except MultipleResultsFound:
            msg = 'There are multiple {} records with the same id={}!'.format(cls.__name__, id)
            log.critical(msg)
            raise MultipleResultsFound(msg)
        except NoResultFound:
            msg = 'There is no record {} with id={}!'.format(cls.__name__, id)
            log.debug(msg)
            raise NoResultFound(msg)
        else:
            return result

    @classmethod
    def all(cls):
        return db_session.query(cls).all()
