from passlib.hash import pbkdf2_sha256 as sha256
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from tensorhive.database import db_session, Base
from tensorhive.models.CRUDModel import CRUDModel
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import validates
from usernames import is_safe_username
from sqlalchemy.ext.hybrid import hybrid_property
import safe
import logging
import re
log = logging.getLogger(__name__)


class PASS_COMPLEXITY:
    TERRIBLE = 0
    SIMPLE = 1
    MEDIUM = 2
    STRONG = 3


USERNAME_WHITELIST = [
    'user'
]


class User(CRUDModel, Base):  # type: ignore
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(40), unique=True, nullable=False)
    email = Column(String(64), unique=False, nullable=False, server_default='<email_missing>')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Managed via property getters and setters
    _hashed_password = Column(String(120), nullable=False)
    _roles = relationship('Role', cascade='all,delete', backref=backref('user'))

    min_password_length = 8

    def check_assertions(self):
        # TODO Check if user has roles assigned
        pass

    def __repr__(self):
        return '<User id={id}, username={username} email={email}>'.format(
            id=self.id, username=self.username, email=self.email)

    @hybrid_property
    def roles(self):
        return self._roles

    @roles.setter  # type: ignore
    def roles(self, new_roles):
        self._roles = new_roles

    @hybrid_property
    def role_names(self):
        return [role.name for role in self._roles]

    def has_role(self, role_name):
        return bool(role_name in self.role_names)

    @hybrid_property
    def password(self):
        return self._hashed_password

    @password.setter  # type: ignore
    def password(self, raw: str):
        result = safe.check(raw, length=self.min_password_length, freq=0, min_types=1, level=PASS_COMPLEXITY.TERRIBLE)
        assert result, 'Incorrect password, reason: {}'.format(result.message)
        self._hashed_password = sha256.hash(raw)

    @validates('username')
    def validate_username(self, key, username):
        assert is_safe_username(username, whitelist=set(USERNAME_WHITELIST)), 'Username unsafe'
        assert 2 < len(username) < 16, 'Username must be between 3 and 15 characters long'
        return username

    @validates('email')
    def validate_email(self, key, email):
        assert re.search("[@.]", email), 'Email not correct'
        assert 3 < len(email) < 64, 'Email must be between 3 and 64 characters long'
        return email

    @classmethod
    def find_by_username(cls, username):
        try:
            result = db_session.query(cls).filter_by(username=username).one()
        except MultipleResultsFound:
            # Theoretically cannot happen because of model built-in constraints
            msg = 'Multiple users with identical usernames has been found!'
            log.critical(msg)
            raise MultipleResultsFound(msg)
        except NoResultFound:
            msg = 'There is no user with username={}!'.format(username)
            log.warning(msg)
            raise NoResultFound(msg)
        else:
            return result

    @property
    def as_dict(self):
        '''Serializes model instance into dict (which is interpreted as json automatically)'''
        try:
            roles = self.role_names
        except Exception:
            roles = []
        finally:
            return {
                'id': self.id,
                'username': self.username,
                'createdAt': self.created_at.isoformat(),
                'roles': roles,
                'email': self.email
            }

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)
