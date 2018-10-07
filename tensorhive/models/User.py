from passlib.hash import pbkdf2_sha256 as sha256
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from tensorhive.database import Base
from tensorhive.models.CRUDModel import CRUDModel
from sqlalchemy.orm import validates
from usernames import is_safe_username
from sqlalchemy.ext.hybrid import hybrid_property
import logging
log = logging.getLogger(__name__)


class User(CRUDModel, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(40), unique=True, nullable=False)
    _hashed_password = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reservations = relationship('Reservation', cascade='all,delete', backref=backref('user'))
    _roles = relationship('Role', cascade='all,delete', backref=backref('user'))
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

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @validates('username')
    def validate_username(self, key, username):
        if not is_safe_username(username):
            raise AssertionError('Invalid username')

        if len(username) < 5 or len(username) > 20:
            raise AssertionError('Username must be between 5 and 20 characters')

        return username

    @property
    def as_dict(self):
        '''Serializes model instance into dict (which is interpreted as json automatically)'''
        return {
            'id': self.id,
            'username': self.username,
            'createdAt': self.created_at.isoformat()
        }

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
