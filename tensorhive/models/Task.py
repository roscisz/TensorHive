from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.utils.DateUtils import DateUtils
import enum
import logging
log = logging.getLogger(__name__)


class TaskStatus(enum.Enum):
    not_running = 1
    running = 2
    terminated = 3
    unsynchronized = 4


class Task(CRUDModel, Base):  # type: ignore
    __tablename__ = 'tasks'
    __public__ = ['id', 'user_id', 'hostname', 'pid', 'command', 'spawn_at', 'terminate_at']

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship(
        'User', backref=backref('tasks', passive_deletes=True, cascade='all, delete, delete-orphan'), lazy='subquery')
    place_in_job_sequence = Column(Integer)
    host = Column(String(40), nullable=False)
    pid = Column(Integer)
    status = Column(Enum(TaskStatus), default=TaskStatus.not_running, nullable=False)
    command = Column(String(400), nullable=False)
    _spawns_at = Column(DateTime)
    _terminates_at = Column(DateTime)

    def __repr__(self):
        return '<Task id={id}, user={user}, name={hostname}, command={command}\n' \
            '\tpid={pid}, status={status}, spawn_at={spawn_at}, terminate_at={terminate_at}>'.format(
                id=self.id,
                user=self.user,
                hostname=self.hostname,
                command=self.command,
                pid=self.pid,
                status=self.status.name)                

    def check_assertions(self):
        pass

    def as_dict(self, include_private=None):
        ret = super(Task, self).as_dict(include_private=include_private)
        ret['status'] = self.status.name
        return ret
