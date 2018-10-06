from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from tensorhive.database import Base, db_session
import logging
log = logging.getLogger(__name__)


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    def save_to_db(self):
        try:
            db_session.add(self)
            db_session.commit()
            log.debug('Created {}'.format(self))
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            log.error(e.__cause__)
            return False

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = cls.query(cls).delete()
            cls.commit()
            return {'message': '{} role(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Deleting all roles operation failed'}

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }