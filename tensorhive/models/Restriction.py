import datetime
import logging

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.database import db_session, Base
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from tensorhive.utils.DateUtils import DateUtils
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.User import User
from tensorhive.models.Group import Group
from tensorhive.models.Resource import Resource
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from typing import List

log = logging.getLogger(__name__)


class Restriction(CRUDModel, Base):  # type: ignore
    """
    Class representing restrictions that permit access to resources only in time specified.
    Restriction is in effect between starts_at and ends_at times. If ends_at is set to NULL, restriction lasts
    indefinitely. If there are schedules assigned to restriction, restriction will be active only in hours specified
    in this schedule (see RestrictionSchedule class for more details). If there are no schedules assigned, restriction
    will be active continuously between starts_at and ends_at dates.
    Restriction should be assigned to certain users or groups to affect them.
    Furthermore, it should be assigned to resources that should be under that restriction. If restriction should apply
    to all resources available, is_global property should be set to true.

    Note: All times and dates are UTC.
    """
    __tablename__ = 'restrictions'
    __table_args__ = {'sqlite_autoincrement': True}
    __public__ = ['id', 'name', 'created_at', 'starts_at', 'ends_at', 'is_global']

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    _created_at = Column('created_at', DateTime, default=datetime.datetime.utcnow)
    _starts_at = Column('starts_at', DateTime, nullable=False)
    _ends_at = Column('ends_at', DateTime)
    is_global = Column(Boolean, nullable=False)

    _users = relationship('User', secondary='restriction2assignee', back_populates='_restrictions')
    _groups = relationship('Group', secondary='restriction2assignee', back_populates='_restrictions')
    _resources = relationship('Resource', secondary='restriction2resource', back_populates='_restrictions')
    _schedules = relationship('RestrictionSchedule', secondary='restriction2schedule', back_populates='_restrictions')

    def __repr__(self):
        return '''<Restriction id={id}
            name={name}
            starts_at={starts_at}
            ends_at={ends_at}
            is_global={is_global}
        '''.format(id=self.id, name=self.name, starts_at=self.starts_at,
                   ends_at=self.ends_at, is_global=self.is_global)

    def check_assertions(self):
        if self.ends_at is not None:
            assert self.ends_at >= self.starts_at, 'End date must happen after the start date!'
            assert self.ends_at > datetime.datetime.utcnow(), 'You are trying to edit restriction that has already' \
                                                              ' expired - please do not do that!'

    @hybrid_property
    def starts_at(self):
        return self._starts_at

    @hybrid_property
    def ends_at(self):
        return self._ends_at

    @hybrid_property
    def created_at(self):
        return self._created_at

    @starts_at.setter  # type: ignore
    def starts_at(self, value: str):
        self._starts_at = DateUtils.try_parse_string(value)
        if self._starts_at is None:
            log.error('Unsupported type (starts_at={})'.format(value))

    @ends_at.setter  # type: ignore
    def ends_at(self, value: str):
        self._ends_at = DateUtils.try_parse_string(value)

    @created_at.setter  # type: ignore
    def created_at(self, value: str):
        self._created_at = DateUtils.try_parse_string(value)
        if self._created_at is None:
            log.error('Unsupported type (created_at={})'.format(value))

    @hybrid_property
    def users(self):
        return self._users

    @hybrid_property
    def groups(self):
        return self._groups

    @hybrid_property
    def resources(self):
        return self._resources

    @hybrid_property
    def schedules(self):
        return self._schedules

    def apply_to_user(self, user: User):
        if user in self.users:
            raise InvalidRequestException('Restriction {restriction} is already being applied to user {user}'
                                          .format(restriction=self, user=user))
        self.users.append(user)
        self.save()

    def remove_from_user(self, user: User):
        if user not in self.users:
            raise InvalidRequestException('User {user} is not affected by restriction {restriction}'
                                          .format(user=user, restriction=self))
        self.users.remove(user)
        self.save()

    def apply_to_group(self, group: Group):
        if group in self.groups:
            raise InvalidRequestException('Restriction {restriction} is already being applied to group {group}'
                                          .format(restriction=self, group=group))
        self.groups.append(group)
        self.save()

    def remove_from_group(self, group: Group):
        if group not in self.groups:
            raise InvalidRequestException('Group {group} is not affected by restriction {restriction}'
                                          .format(group=group, restriction=self))
        self.groups.remove(group)
        self.save()

    def apply_to_resource(self, resource: Resource):
        if resource in self.resources:
            raise InvalidRequestException('Restriction {restriction} is already being applied to resource {resource}'
                                          .format(restriction=self, resource=resource))
        self.resources.append(resource)
        self.save()

    def apply_to_resources(self, resources: List[Resource]):
        for resource in resources:
            if resource in self.resources:
                # Skip adding resource that was already there
                continue
            self.resources.append(resource)
        self.save()

    def remove_from_resource(self, resource: Resource):
        if resource not in self.resources:
            raise InvalidRequestException('Resource {resource} is not affected by restriction {restriction}'
                                          .format(resource=resource, restriction=self))
        self.resources.remove(resource)
        self.save()

    def remove_from_resources(self, resources: List[Resource]):
        for resource in resources:
            if resource not in self.resources:
                # Skip removing resource that wasn't there
                continue
            self.resources.remove(resource)
        self.save()

    def add_schedule(self, schedule: RestrictionSchedule):
        if schedule in self.schedules:
            raise InvalidRequestException('Schedule {schedule} is already being applied to restriction {restriction}'
                                          .format(schedule=schedule, restriction=self))
        self.schedules.append(schedule)
        self.save()

    def remove_schedule(self, schedule: RestrictionSchedule):
        if schedule not in self.schedules:
            raise InvalidRequestException('Schedule {schedule} is not assigned to restriction {restriction}'
                                          .format(schedule=schedule, restriction=self))
        self.schedules.remove(schedule)
        self.save()

    def get_all_affected_users(self):
        """Will return all users affected by this restriction, i.e. users directly assigned to this restriction
        and members of all groups assigned to this restriction."""
        affected_users = self.users[:]
        for group in self.groups:
            affected_users.extend(group.users)
        return list(set(affected_users))

    @classmethod
    def get_global_restrictions(cls, include_expired=False):
        query = db_session.query(Restriction).filter(Restriction.is_global.is_(True))
        if not include_expired:
            query.filter(Restriction.is_expired is False)
        return query.all()

    @property
    def is_active(self):
        now = datetime.datetime.utcnow()
        active = self.starts_at <= now and not self.is_expired
        if not self.schedules:  # no custom schedules
            return active

        active_schedules = [schedule for schedule in self.schedules if schedule.is_active]
        return active and len(active_schedules) > 0

    @property
    def is_expired(self):
        now = datetime.datetime.utcnow()
        return self.ends_at is not None and self.ends_at <= now

    def as_dict(self, include_groups=False, include_users=False, include_resources=False, include_private=False):
        ret = super(Restriction, self).as_dict(include_private=include_private)
        ret['schedules'] = [schedule.as_dict() for schedule in self.schedules]

        if include_groups:
            ret['groups'] = [group.as_dict(include_users=False) for group in self.groups]
        if include_users:
            # do not include user's groups, as they are insignificant considering the scope of the restriction
            ret['users'] = [user.as_dict(include_groups=False) for user in self.users]
        if include_resources:
            ret['resources'] = [resource.as_dict() for resource in self.resources]
        return ret


class Restriction2Assignee(Base):  # type: ignore
    __tablename__ = 'restriction2assignee'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    restriction_id = Column(Integer, ForeignKey('restrictions.id', ondelete='CASCADE'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))


class Restriction2Resource(Base):  # type: ignore
    __tablename__ = 'restriction2resource'

    restriction_id = Column(Integer, ForeignKey('restrictions.id', ondelete='CASCADE'), primary_key=True)
    resource_id = Column(String(64), ForeignKey('resources.id', ondelete='CASCADE'), primary_key=True)
