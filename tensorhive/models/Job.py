from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text, Boolean
from datetime import datetime, timedelta
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.Task import Task, TaskStatus
from tensorhive.utils.DateUtils import DateUtils
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from typing import Optional, Union, List
import enum
import logging
log = logging.getLogger(__name__)


class JobStatus(enum.Enum):
    not_running = 1
    running = 2
    terminated = 3
    unsynchronized = 4
    pending = 5


class Job(CRUDModel, Base):  # type: ignore
    __tablename__ = 'jobs'
    __table_args__ = {'sqlite_autoincrement': True}
    __public__ = ['id', 'name', 'description', 'user_id', 'start_at', 'stop_at']

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship("User", back_populates="_jobs")
    _status = Column(Enum(JobStatus), default=JobStatus.not_running, nullable=False)
    _start_at = Column(DateTime)
    _stop_at = Column(DateTime)
    is_queued = Column(Boolean)

    _tasks = relationship(
        'Task', cascade='all, delete', back_populates="job", lazy='subquery')

    def __repr__(self):
        return '<Job id={id}, name={name}, description={description}, user={user_id}, status={status}>'.format(
            id=self.id,
            name=self.name,
            description=self.description,
            user_id=self.user_id,
            status=self._status.name)

    def check_assertions(self):
        if self.stop_at is not None and self.start_at is not None:
            assert self.stop_at >= self.start_at, 'Time of the end must happen after the start!'

    @hybrid_property
    def tasks(self):
        return self._tasks

    @hybrid_property
    def number_of_tasks(self):
        return len(self._tasks)

    @hybrid_property
    def status(self):
        return self._status

    def add_task(self, task: Task):
        if task in self.tasks:
            raise InvalidRequestException('Task {task} is already assigned to job {job}!'
                                          .format(task=task, job=self))
        self.tasks.append(task)
        self.synchronize_status()
        self.save()

    def remove_task(self, task: Task):
        if task not in self.tasks:
            raise InvalidRequestException('Task {task} is not assigned to job {job}!'
                                          .format(task=task, job=self))
        self.tasks.remove(task)
        self.save()

    def synchronize_status(self):
        """ Job status is synchronized on every change of one of its tasks status
        """
        status_pre = self._status

        statuses = [task.status for task in self.tasks]
        if TaskStatus.unsynchronized in statuses and self._status is not JobStatus.pending:
            self._status = JobStatus.unsynchronized
        elif TaskStatus.running in statuses:
            self._status = JobStatus.running
        elif TaskStatus.terminated in statuses:
            self._status = JobStatus.terminated
        elif TaskStatus.not_running in statuses:
            self._status = JobStatus.not_running

        if status_pre is JobStatus.running and self._status is JobStatus.not_running:
            self.is_queued = False

        self.save()

    def enqueue(self):
        assert self.status is not JobStatus.pending, 'Cannot enqueue job that is already pending'

        statuses = [task.status for task in self.tasks]
        assert TaskStatus.running not in statuses, 'Cannot enqueue job that contains running tasks'

        self.is_queued = True
        self._status = JobStatus.pending
        self.save()

    def dequeue(self):
        assert self._status == JobStatus.pending

        self.is_queued = False
        self._status = JobStatus.not_running
        self.save()

    @hybrid_property
    def start_at(self):
        return self._start_at

    @start_at.setter  # type: ignore
    def start_at(self, value):
        if value is not None:
            self._start_at = DateUtils.try_parse_string(value)
            if self._start_at is None:
                log.error('Unsupported type (start_at={})'.format(value))
            else:
                assert self._start_at > datetime.utcnow(), 'Job start time must be in the future!'
        else:
            self._start_at = None

    @hybrid_property
    def stop_at(self):
        return self._stop_at

    @stop_at.setter  # type: ignore
    def stop_at(self, value):
        if value is not None:
            self._stop_at = DateUtils.try_parse_string(value)
            if self._stop_at is None:
                log.error('Unsupported type (start_at={})'.format(value))
        else:
            self._stop_at = None

    def as_dict(self, include_private=None):
        ret = super(Job, self).as_dict(include_private=include_private)
        ret['status'] = self._status.name
        return ret

    @staticmethod
    def get_job_queue() -> List['Job']:
        return Job.query.filter(Job.is_queued).filter(Job.status != JobStatus.running).all()

    @staticmethod
    def get_jobs_running_from_queue() -> List['Job']:
        return Job.query.filter(Job.is_queued).filter(Job.status == JobStatus.running).all()
