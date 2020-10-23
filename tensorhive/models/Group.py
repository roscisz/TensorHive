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
    _is_default = Column('is_default', Boolean, nullable=True, unique=True)  # Should be True or None, never False

    _users = relationship('User', secondary='user2group')
    _restrictions = relationship('Restriction', secondary='restriction2assignee')

    def __repr__(self):
        return '<Group id={id}, name={name}>'.format(id=self.id, name=self.name)

    def check_assertions(self):
        assert self._is_default is None or self._is_default is True, 'is_default should be either set to True for' \
                                                                     'the default group or None for the rest'

    @hybrid_property
    def users(self):
        return self._users

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
            'createdAt': DateUtils.stringify_datetime(self.created_at)
        }
        if include_users:
            group['users'] = [user.as_dict_shallow for user in self.users]
        return group

    @classmethod
    def get_default_group(cls):
        """
        :raises: MultipleResultsFound if more than one default group is found
        :return: A group that is marked as default or None if no such group exists
        """
        return Group.query.filter(Group.is_default.is_(True)).one_or_none()

    @classmethod
    def set_default_group(cls, group_id):
        """
        Sets the group with id = group_id as a default group.
        Will also unmark the existing default group as the default.
        :raises: NoResultFound if group with given id doesn't exist.
        :return: The default group.
        """
        try:
            group = Group.get(group_id)
        except NoResultFound as e:
            raise e

        cls.delete_default_group_if_exists()
        group.is_default = True
        return group.save()

    @classmethod
    def delete_default_group_if_exists(cls):
        """
        Will mark the default group as non-default. If no such group exists, no action will be taken.
        :return: True if group was marked as non-default, False if no default group was found.
        """
        group = cls.get_default_group()
        if group is None:
            return False
        group.is_default = None
        group.save()
        return True


class User2Group(Base):  # type: ignore
    __tablename__ = 'user2group'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow())

    user = relationship('User', backref=backref('user2group', cascade='all,delete-orphan'))
    group = relationship('Group', backref=backref('user2group', cascade='all,delete-orphan'))
