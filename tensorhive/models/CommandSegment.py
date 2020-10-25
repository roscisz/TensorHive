from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from tensorhive.database import Base
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
    actual_command = 3


class CommandSegment(CRUDModel, Base):  # type: ignore
    __tablename__ = 'command_segments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    _segment_type = Column(Enum(SegmentType), default=SegmentType.env_variable, nullable=False)

    def __repr__(self):
        return '<Segment id={id}, name={name}, type={type}>'.format(
                id=self.id,
                name=self.name,
                type=self.segment_type
                )                


    def check_assertions(self):
        pass

    @hybrid_property
    def segment_type(self):
        return self._segment_type
"""
    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': 'env_var'
#TODO segment_type parsing
        }
"""

class CommandSegment2Task(Base):  # type: ignore
    __tablename__ = 'cmd_segment2task'

    task_id = Column(Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    cmd_segment_id = Column(Integer, ForeignKey('command_segments.id', ondelete='CASCADE'), primary_key=True)
    _value = Column(String(100))
    _index = Column(Integer) # , nullable=False positive - parameters; negative - env variables; 0 - actual command

    @hybrid_property
    def value(self):
        return self._value

    @hybrid_property
    def index(self):
        return self._index

    @index.setter
    def index(self, value: Integer):
        self._index = index
        if self._index is None:
            log.error('Unsupported type (index={})'.format(index))

    @value.setter
    def value(self, value: String):
        self._value = value