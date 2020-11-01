from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text
from datetime import datetime
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.Task import Task
from tensorhive.utils.DateUtils import DateUtils
from typing import Optional, Union
import enum
import logging
log = logging.getLogger(__name__)

class JobStatus(enum.Enum):
    not_running = 1
    running = 2
    terminated = 3
    unsynchronized = 4

class Job(CRUDModel, Base):  # type: ignore
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), unique=True, nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    status = Column(Enum(JobStatus), default=JobStatus.not_running, nullable=False)
    _start_at = Column(DateTime)
    _end_at = Column(DateTime)

    _tasks = relationship(
        'Task', backref=backref('job', single_parent=True, cascade='all, delete-orphan'), lazy='subquery')


    def __repr__(self):
        return '<Job id={id}, name={name}, description={description}, user={user_id}, status={status}, start_at={start_at}, end_at={end_at}>'.format(
                id=self.id,
                name=self.name,
                description=self.description,
                user_id=self.user_id,
                status=self.status.name,               
                start_at=self.start_at,
                end_at=self.end_at)

    def check_assertions(self):
        if self.end_at is not None and self.start_at is not None:
            assert self.end_at >= self.start_at, 'Time of the end must happen after the start!'
            assert self.end_at > datetime.datetime.utcnow(), 'You are trying to edit time of the job that has already ended'
        
        if self.end_at is not None:
            assert self.start_at is not None, 'If end time of the job is known, start time has to be known too'

    @hybrid_property
    def tasks(self):
        return self._tasks

    @hybrid_property
    def number_of_tasks(self):
        return len(self._tasks)

    def add_task(self, task: Task):
        if task in self.tasks:
            raise Exception('Task {task} is already assigned to job {job}!'
                                          .format(task=task, job=self))
        self.tasks.append(task)
        self.save()

    def remove_task(self, task: Task):
        if task not in self.tasks:
            raise Exception('Task {task} is not assigned to job {job}!'
                                          .format(task=task, job=self))

        self.tasks.remove(task)
        self.save()

    @hybrid_property
    def start_at(self):
        return self._start_at
    
    @hybrid_property
    def end_at(self):
        return self._end_at

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'userId': self.user_id,
            'status': self.status.name,
            'startAt': DateUtils.try_parse_datetime(self.start_at),
            'endAt': DateUtils.try_parse_datetime(self.end_at)
        }
