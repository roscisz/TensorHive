from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from tensorhive.database import Base, db_session
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.models.CRUDModel import CRUDModel
from typing import Optional, Union
import logging
import enum
log = logging.getLogger(__name__)


class SegmentType(enum.Enum):
    env_variable = 1
    parameter = 2


class CommandSegment(CRUDModel, Base):  # type: ignore
    __tablename__ = 'command_segments'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    _segment_type = Column('segment_type', Enum(SegmentType), default=SegmentType.env_variable, nullable=False)
    _tasks = relationship('Task', secondary='cmd_segment2task', back_populates='_cmd_segments')

    def __repr__(self):
        return '<Segment id={id}, name={name}, type={type}>'.format(
            id=self.id,
            name=self.name,
            type=self.segment_type)

    def check_assertions(self):
        pass

    @hybrid_property
    def segment_type(self):
        return self._segment_type

    @hybrid_property
    def tasks(self):
        return self._tasks

    @classmethod
    def find_by_name(cls, name):
        try:
            result = db_session.query(cls).filter_by(name=name).one()
        except MultipleResultsFound:
            # Theoretically cannot happen because of model built-in constraints
            msg = 'Multiple command segments with identical names has been found!'
            log.critical(msg)
            raise MultipleResultsFound(msg)
        except NoResultFound:
            msg = 'There is no command segment with name={}!'.format(name)
            log.warning(msg)
            raise NoResultFound(msg)
        else:
            return result


class CommandSegment2Task(Base):  # type: ignore
    __tablename__ = 'cmd_segment2task'

    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    cmd_segment_id = Column(Integer, ForeignKey('command_segments.id', ondelete='CASCADE'), primary_key=True)
    _value = Column(String(100))
    _index = Column(Integer)  # positive - parameters; negative - env variables

    @hybrid_property
    def index(self):
        return self._index

    @hybrid_property
    def value(self):
        return self._value
