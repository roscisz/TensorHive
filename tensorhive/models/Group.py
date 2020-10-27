import datetime
import logging

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.database import Base
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.RestrictionAssignee import RestrictionAssignee
from tensorhive.models.User import User
from tensorhive.utils.DateUtils import DateUtils

log = logging.getLogger(__name__)


class Group(CRUDModel, RestrictionAssignee):  # type: ignore
    __tablename__ = 'groups'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), unique=False, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    _is_default = Column('is_default', Boolean)

    _users = relationship('User', secondary='user2group')
    _restrictions = relationship('Restriction', secondary='restriction2assignee')

    def __repr__(self):
        return '<Group id={id}, name={name}>'.format(id=self.id, name=self.name)

    def check_assertions(self):
        pass

    @hybrid_property
    def is_default(self):
        return self._is_default if self._is_default is not None else False

    @hybrid_property
    def users(self):
        return self._users

    @is_default.setter
    def is_default(self, value):
        self._is_default = value

    def add_user(self, user: User):
        if user in self.users:
            raise InvalidRequestException('User {user} is already a member of group {group}!'
                                          .format(user=user, group=self))
        self.users.append(user)
        self.save()

    def remove_user(self, user: User):
        if user not in self.users:
            raise InvalidRequestException('User {user} is not a member of group {group}!'
                                          .format(user=user, group=self))

        self.users.remove(user)
        self.save()

    @hybrid_property
    def as_dict(self):
        """
        Serializes current instance into dict.
        :return: Dictionary representing current instance.
        """
        return self._as_dict(True)

    @hybrid_property
    def as_dict_shallow(self):
        """
        Serializes current instance into dict. Will not include group's users (to prevent recurrence).
        :return: Dictionary representing current instance (without users).
        """
        return self._as_dict(False)

    def _as_dict(self, include_users):
        group = {
            'id': self.id,
            'name': self.name,
            'createdAt': DateUtils.stringify_datetime(self.created_at),
            'isDefault': self.is_default
        }
        if include_users:
            group['users'] = [user.as_dict_shallow for user in self.users]
        return group

    @classmethod
    def get_default_groups(cls):
        """
        :return: List of groups that are marked as default.
        """
        return Group.query.filter(Group._is_default.is_(True)).all()


class User2Group(Base):  # type: ignore
    __tablename__ = 'user2group'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow())

    user = relationship('User', backref=backref('user2group', cascade='all,delete-orphan'))
    group = relationship('Group', backref=backref('user2group', cascade='all,delete-orphan'))
