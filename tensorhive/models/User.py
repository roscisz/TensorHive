from passlib.hash import pbkdf2_sha256 as sha256
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship, backref
from tensorhive.database import db_session
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.RestrictionAssignee import RestrictionAssignee
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


class User(CRUDModel, RestrictionAssignee):  # type: ignore
    __tablename__ = 'users'
    __public__ = ['id', 'username', 'created_at']
    __private__ = ['email']

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(40), unique=True, nullable=False)
    email = Column(String(64), unique=False, nullable=False, server_default='<email_missing>')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Managed via property getters and setters
    _hashed_password = Column(String(120), nullable=False)
    _roles = relationship('Role', cascade='all,delete', backref=backref('user'))
    _groups = relationship('Group', secondary='user2group', back_populates='_users', viewonly=True)
    _restrictions = relationship('Restriction', secondary='restriction2assignee', back_populates='_users',
                                 viewonly=True)
    _reservations = relationship('Reservation', cascade='all,delete')

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
    def groups(self):
        return self._groups

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

    def as_dict(self, include_private=False, include_groups=True):
        """
        Serializes current instance into dict.
        :param include_private: passed to CRUDModel as_dict
        :param include_groups: flag determining if user groups should be included (False to prevent recurrence)
        :return: Dictionary representing current instance.
        """
        user = super(User, self).as_dict(include_private)

        try:
            roles = self.role_names
        except Exception:
            roles = []
        finally:
            user['roles'] = roles
            if include_groups:
                user['groups'] = [group.as_dict(include_users=False) for group in self.groups]
            return user

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def get_restrictions(self, include_expired=False, include_group=False):
        restrictions = super(User, self).get_restrictions(include_expired=include_expired)
        if include_group:
            for group in self.groups:
                restrictions = restrictions + group.get_restrictions(include_expired=include_expired)
        return list(set(restrictions))

    def get_active_restrictions(self, include_group=False):
        restrictions = super(User, self).get_active_restrictions()
        if include_group:
            for group in self.groups:
                restrictions = restrictions + group.get_active_restrictions()
        return list(set(restrictions))

    def get_reservations(self, include_cancelled=False):
        return self._reservations if include_cancelled else [r for r in self._reservations if not r.is_cancelled]

    def filter_infrastructure_by_user_restrictions(self, infrastructure):
        not_allowed_hostnames = []
        allowed_gpus = []
        for restriction in self.get_restrictions(include_expired=False, include_group=True):
            # If restriction is global user has permissions to all resources
            if restriction.is_global:
                return infrastructure
            allowed_gpus.extend([resource.id for resource in restriction.resources])
        allowed_gpus = set(allowed_gpus)
        for hostname, value in infrastructure.items():
            gpu_list = value.get('GPU')
            if gpu_list is not None:
                all_gpus = set(gpu_list.keys())
                not_allowed_gpus = all_gpus - allowed_gpus
                for key in not_allowed_gpus:
                    del gpu_list[key]
            if gpu_list is None or len(gpu_list) == 0:
                not_allowed_hostnames.append(hostname)
        for hostname in not_allowed_hostnames:
            del infrastructure[hostname]
        return infrastructure
