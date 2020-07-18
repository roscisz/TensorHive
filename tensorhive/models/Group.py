import datetime
import logging

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.database import Base
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.User import User
from tensorhive.models.RestrictionAssignee import RestrictionAssignee

log = logging.getLogger(__name__)


class Group(CRUDModel, RestrictionAssignee):  # type: ignore
    __tablename__ = 'groups'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), unique=False, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    _users = relationship('User', secondary='user2group')
    _restrictions = relationship('Restriction', secondary='restriction2assignee')

    def __repr__(self):
        return '<Group id={id}, name={name}>'.format(id=self.id, name=self.name)

    def check_assertions(self):
        pass

    @hybrid_property
    def users(self):
        return self._users

    def add_user(self, user: User):
        self.users.append(user)
        self.save()

    def remove_user(self, user: User):
        self.users.remove(user)
        self.save()

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'createdAt': self.created_at.isoformat(),
            'users': self.users
        }


class User2Group(Base):  # type: ignore
    __tablename__ = 'user2group'
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow())

    user = relationship('User', backref=backref('user2group', cascade='all,delete-orphan'))
    group = relationship('Group', backref=backref('user2group', cascade='all,delete-orphan'))
