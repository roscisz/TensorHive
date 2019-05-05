from sqlalchemy import Column, Integer, String, ForeignKey, Enum
#from sqlalchemy.exc import SQLAlchemyError
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from tensorhive.models.CRUDModel import CRUDModel
import enum
import logging
log = logging.getLogger(__name__)


class TaskStatus(enum.Enum):
    not_running = 1
    running = 2
    terminated = 3
    unsynchronized = 4


class Task(CRUDModel, Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship(
        'User', backref=backref('tasks', passive_deletes=True, cascade='all, delete, delete-orphan'), lazy='subquery')
    host = Column(String(40), nullable=False)
    pid = Column(Integer, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.not_running, nullable=False)
    command = Column(String(400), nullable=False)

    def __repr__(self):
        return '<Task id={id}, user={user}, hostname={hostname}, command={command}\n' \
            '\tpid={pid}, status={status}>'.format(
            id=self.id,
            user=self.user,
            hostname=self.host,
            command=self.command,
            pid=self.pid,
            status=self.status.name)

    def check_assertions(self):
        pass

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'hostname': self.host,
            'pid': self.pid,
            'status': self.status.name,
            'command': self.command
        }