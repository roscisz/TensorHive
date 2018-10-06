from passlib.hash import pbkdf2_sha256 as sha256
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import Base, db_session
import logging
log = logging.getLogger(__name__)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(40), unique=True, nullable=False)
    _hashed_password = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reservations = relationship('Reservation', backref='user')
    _roles = relationship('Role', cascade='all,delete', backref='user')
    # TODO Default role

    def __repr__(self):
        return '<User id={id}, username={username}>'.format(
            id=self.id, 
            username=self.username)

    @property
    def roles(self):
        return self._roles

    @property
    def role_names(self):
        return [role.name for role in self._roles]

    def has_role(self, role_name):
        return bool(role_name in self.role_names)

    @property
    def password(self):
        return self._hashed_password

    @password.setter
    def password(self, raw_password: str):
        self._hashed_password = sha256.hash(raw_password)

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

    def delete_from_db(self):
        try:
            db_session.delete(self)
            db_session.commit()
            log.debug('Deleted {}'.format(self))
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            log.error(e.__cause__)
            return False

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @property
    def as_dict(self):
        '''Serializes model instance into dict (which is interpreted as json automatically)'''
        return {
            'id': self.id,
            'username': self.username,
            'createdAt': self.created_at.isoformat()
        }

    # Not implemented yet
    # @classmethod
    # def get_count(cls):
    #     count_q = self.statement.with_only_columns([func.count()]).order_by(None)
    #     count = q.session.execute(count_q).scalar()
    #     return count

    #     users_list = list(map(lambda user: as_json(user), all_users))
    #     return {'users': users_list}

    # @classmethod
    # def delete_all(cls):
    #     try:
    #         num_rows_deleted = db.session.query(cls).delete()
    #         db.session.commit()
    #         return {'message': '{} user(s) deleted'.format(num_rows_deleted)}
    #     except:
    #         return {'message': 'Deleting all users operation failed'}

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
