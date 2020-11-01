from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.CommandSegment import SegmentType, CommandSegment
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
#    place_in_job_sequence = Column(Integer)
    host = Column(String(40), nullable=False)
    pid = Column(Integer)
    status = Column(Enum(TaskStatus), default=TaskStatus.not_running, nullable=False)
    command = Column(String(400), nullable=False)
    _spawns_at = Column(DateTime)
    _terminates_at = Column(DateTime)
    _cmd_segments = relationship('CommandSegment', secondary='cmd_segment2task', 
                            backref=backref('tasks'))
#TODO delete "free" children (free segments after Task is deleted)

    def __repr__(self):
        return '<Task id={id}, job={job}, user={user}, name={host}, command={command}\n' \
            '\tpid={pid}, status={status}>'.format(
                id=self.id,
                job=self.job,
                user=self.user,
#                place_in_jobseq=self.place_in_job_sequence,
                host=self.host,
                command=self.command,
                pid=self.pid,
                status=self.status.name)                

    def check_assertions(self):
        pass

    @hybrid_property
    def cmd_segments(self):
        return self._cmd_segments

    @hybrid_property
    def number_of_params(self):
        params = 0
        for segment in self.cmd_segments:
            if segment.segment_type == SegmentType.parameter:
                params = params + 1
        return params

    @hybrid_property
    def number_of_env_vars(self):
        env_variables = 0
        for segment in self.cmd_segments:
            if segment.segment_type == SegmentType.env_variable:
                env_variables = env_variables + 1
        return env_variables

    @hybrid_property
    def actual_command(self):
        actual_command = 0
        for segment in self.cmd_segments:
            if segment.segment_type == SegmentType.actual_command:
                return segment
        return None 

    def add_cmd_segment(self, cmd_segment: CommandSegment):
        if cmd_segment in self.cmd_segments:
            raise Exception('Segment {cmd_segment} is already assigned to task {task}!'
                                          .format(cmd_segment=cmd_segment, task=self))
        self.cmd_segments.append(cmd_segment)
        self.save()

    def remove_cmd_segment(self, cmd_segment: CommandSegment):
        if cmd_segment not in self.cmd_segments:
            raise Exception('Segment {cmd_segment} is not assigned to task {task}!'
                                          .format(cmd_segment=cmd_segment, task=self))

        self.cmd_segments.remove(cmd_segment)
        self.save()


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
#            'placeInSeq': self.place_in_job_sequence,
            'hostname': self.host,
            'pid': self.pid,
            'status': self.status.name,
            'command': self.command,
            'spawnAt': DateUtils.try_stringify_datetime(self.spawn_at),
            'terminateAt': DateUtils.try_stringify_datetime(self.terminate_at)
        }
