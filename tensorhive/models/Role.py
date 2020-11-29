from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from tensorhive.database import db_session, Base
from tensorhive.models.CRUDModel import CRUDModel
import logging
log = logging.getLogger(__name__)


class Role(CRUDModel, Base):  # type: ignore
    __tablename__ = 'roles'
    __public__ = ['id', 'name']

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    def check_assertions(self):
        pass

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
        except Exception:
            return {'message': 'Deleting all roles operation failed'}

    def as_dict(self, include_private=False):
        ret = super(Role, self).as_dict(include_private=include_private)
        ret['user_id'] = self.user_id
        return ret
