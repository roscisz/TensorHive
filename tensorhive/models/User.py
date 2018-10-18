from passlib.hash import pbkdf2_sha256 as sha256
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from tensorhive.database import db, flask_app
from tensorhive.models.CRUDModel import CRUDModel
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import validates
from usernames import is_safe_username
from sqlalchemy.ext.hybrid import hybrid_property
import safe
import logging
log = logging.getLogger(__name__)


class PASS_COMPLEXITY:
        TERRIBLE = 0
        SIMPLE = 1
        MEDIUM = 2
        STRONG = 3


class User(CRUDModel, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(40), unique=True, nullable=False)
    #siema = Column(String(40))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    reservations = relationship('Reservation', cascade='all,delete', backref=backref('user'))

    # Managed via property getters and setters
    _hashed_password = Column(String(120), nullable=False)
    _roles = relationship('Role', cascade='all,delete', backref=backref('user'))

    def check_assertions(self):
        # TODO Check if user has roles assigned
        pass
     
    def __repr__(self):
        return '<User id={id}, username={username}>'.format(
            id=self.id, 
            username=self.username)

    @hybrid_property
    def roles(self):
        return self._roles

    @roles.setter
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

    @password.setter
    def password(self, raw: str):
        result = safe.check(raw, length=8, freq=0, min_types=1, level=PASS_COMPLEXITY.TERRIBLE)
        assert result, 'Incorrect password, reason: {}'.format(result.message)
        self._hashed_password = sha256.hash(raw)

    @validates('username')
    def validate_username(self, key, username):
        assert is_safe_username(username), 'Invalid username'
        assert 4 < len(username) < 30, 'Username must be between 4 and 30 characters long!'
        return username

    @classmethod
    def find_by_username(cls, username):
        with flask_app.app_context():
            try:
                result = db.session.query(cls).filter_by(username=username).one()
            except MultipleResultsFound as e:
                # Theoretically cannot happen because of model built-in constraints
                msg = 'Multiple users with identical usernames has been found!'
                log.critical(msg)
                raise MultipleResultsFound(msg)
            except NoResultFound as e:
                msg = 'There is no user with username={}!'.format(username)
                log.warning(msg)
                raise NoResultFound(msg)
            else:
                return result

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
