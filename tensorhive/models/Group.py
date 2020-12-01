import datetime
import logging

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.database import Base
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.RestrictionAssignee import RestrictionAssignee
from tensorhive.models.User import User

log = logging.getLogger(__name__)


class Group(CRUDModel, RestrictionAssignee):  # type: ignore
    __tablename__ = 'groups'
    __table_args__ = {'sqlite_autoincrement': True}
    __public__ = ['id', 'name', 'is_default', 'created_at']

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), unique=False, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    _is_default = Column('is_default', Boolean)

    _users = relationship('User', secondary='user2group', back_populates='_groups')
    _restrictions = relationship('Restriction', secondary='restriction2assignee', back_populates='_groups',
                                 viewonly=True)

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

    @is_default.setter  # type: ignore
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

    def as_dict(self, include_private=False, include_users=True):
        """
        Serializes current instance into dict. Will not include group's users (to prevent recurrence).
        :param include_private: passed to CRUDModel as_dict
        :param include_users: flag that determines if users should be included (False to prevent recurrence)
        :return: Dictionary representing current instance (without users).
        """
        group = super(Group, self).as_dict(include_private=include_private)
        if include_users:
            group['users'] = [user.as_dict(include_groups=False) for user in self.users]
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
