from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import Base, db_session
import logging
log = logging.getLogger(__name__)

class RoleModel(Base):
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

    @classmethod
    def return_all(cls):
        all_roles = RoleModel.query.all()
        roles_list = [role.as_dict for role in list(all_roles)]
        return {'roles': roles_list}

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }