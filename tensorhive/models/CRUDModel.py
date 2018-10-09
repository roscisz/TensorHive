from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from tensorhive.database import db
import logging
log = logging.getLogger(__name__)


class CRUDModel:

    def check_assertions(self):
        '''
        Purpose of this method is to run all necessary validation
        before creating and saving model instance to the database.

        Validation methods should raise AssertionError on failure
        '''
        # raise NotImplementedError('Method must be overriden')
        pass

    # @classmethod
    # def create(cls, **kwargs):
    #     try:
    #         new_object = cls(**kwargs)
    #     except AssertionError as e:
    #         raise e
    #     else:
    #         return new_object

    def save(self):
        try:
            self.check_assertions()
            db.session.add(self)
            db.session.commit()
        # OperationalError
        except SQLAlchemyError as e:
            db.session.rollback()
            log.error('{cause} with {data}'.format(cause=e.__cause__, data=self))
            raise e
        except AssertionError as e:
            raise e
        else:
            log.debug('Created {}'.format(self))
            return self

    def destroy(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            log.error('{} with {}'.format(cause=e.__cause__, data=self))
            raise e
        else:
            log.debug('Deleted {}'.format(self))
            return self

    @classmethod
    def get(cls, id):
        try:
            result = db.session.query(cls).filter_by(id=id).one()
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
