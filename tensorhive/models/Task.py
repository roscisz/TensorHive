from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
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
        return '<Task id={id}, job={job}, user={user}, place_in_jobseq={place_in_jobseq}, name={host}, command={command}\n' \
            '\tpid={pid}, status={status}>'.format(
                id=self.id,
                job=self.job,
                user=self.user,
                place_in_jobseq=self.place_in_job_sequence,
                host=self.host,
                command=self.command,
                pid=self.pid,
                status=self.status.name)                

    def check_assertions(self):
        pass

    @hybrid_property
    def spawns_at(self):
        return self._spawns_at

    @hybrid_property
    def terminates_at(self):
        return self._terminates_at

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'jobId': self.job_id,
            'userId': self.user_id,
            'placeInSeq': self.place_in_job_sequence,
            'hostname': self.host,
            'pid': self.pid,
            'status': self.status.name,
            'command': self.command,
            'spawnsAt': DateUtils.try_parse_datetime(self._spawns_at),
            'terminatesAt': DateUtils.try_parse_datetime(self._terminates_at)
        }