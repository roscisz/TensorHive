from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from tensorhive.database import db, flask_app
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
        with flask_app.app_context():
            try:
                self.check_assertions()
                db.session.add(self)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                log.error('{cause} with {data}'.format(cause=e.__cause__, data=self))
                raise
            except AssertionError as e:
                log.error(e)
                raise
            except Exception as e:
                log.critical(type(e))
                raise
            else:
                log.debug('Created {}'.format(self))
                return self

    def destroy(self):
        with flask_app.app_context():
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
        with flask_app.app_context():
            try:
                result = db.session.query(cls).filter_by(id=id).one()
            except MultipleResultsFound as e:
                msg = 'There are multiple {} records with the same id={}!'.format(cls.__name__, id)
                log.critical(msg)
                raise MultipleResultsFound(msg)
            except NoResultFound as e:
                msg = 'There is no record {} with id={}!'.format(cls.__name__, id)
                log.warning(msg)
                raise NoResultFound(msg)
            else:
                return result

    @classmethod
    def all(cls):
        with flask_app.app_context():
            return db.session.query(cls).all()
