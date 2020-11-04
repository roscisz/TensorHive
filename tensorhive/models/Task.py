from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.CommandSegment import SegmentType, CommandSegment, CommandSegment2Task
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
    host = Column(String(40), nullable=False)
    pid = Column(Integer)
    status = Column(Enum(TaskStatus), default=TaskStatus.not_running, nullable=False)
    command = Column(String(400), nullable=False)
    _spawns_at = Column(DateTime)
    _terminates_at = Column(DateTime)
    _cmd_segments = relationship('CommandSegment', secondary='cmd_segment2task', back_populates='_tasks')

# TODO write tests for cascade CommandSegment delete when Task is deleted

    def __repr__(self):
        return '<Task id={id}, jobId={job_id}, name={host}, command={command}\n' \
            '\tpid={pid}, status={status}>'.format(
                id=self.id,
                job_id=self.job_id,
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
        for segment in self.cmd_segments:
            if segment.segment_type == SegmentType.actual_command:
                link = self.get_cmd_segment_link(segment)
                actual_command = link.value
                return actual_command
        return ''

    def get_cmd_segment_link(self, cmd_segment: CommandSegment):
        """returns connection between task and its command segment"""
        if cmd_segment not in self.cmd_segments:
            raise Exception('Segment {cmd_segment} is not assigned to task {task}!'
                            .format(cmd_segment=cmd_segment, task=self))
        link = CommandSegment2Task.query.filter(CommandSegment2Task.cmd_segment_id == cmd_segment.id, 
                                                CommandSegment2Task.task_id == self.id).one()
        return link

    def add_cmd_segment(self, cmd_segment: CommandSegment, value: String):
        if cmd_segment in self.cmd_segments:
            raise Exception('Segment {cmd_segment} is already assigned to task {task}!'
                            .format(cmd_segment=cmd_segment, task=self))
        self.cmd_segments.append(cmd_segment)
        self.save()
        link = self.get_cmd_segment_link(cmd_segment)
        if cmd_segment.segment_type == SegmentType.env_variable:
            setattr(link, '_index', -self.number_of_env_vars)
        elif cmd_segment.segment_type == SegmentType.parameter:
            setattr(link, '_index', self.number_of_params)
        elif cmd_segment.segment_type == SegmentType.actual_command:
            setattr(link, '_index', 0)
        setattr(link, '_value', value)

    def remove_cmd_segment(self, cmd_segment: CommandSegment):
        if cmd_segment not in self.cmd_segments:
            raise Exception('Segment {cmd_segment} is not assigned to task {task}!'
                            .format(cmd_segment=cmd_segment, task=self))
        link = get_cmd_segment_link(cmd_segment)
        removed_index = link.index
        self.cmd_segments.remove(cmd_segment)

        for segment in self.cmd_segments:
            link = get_cmd_segment_link(segment)
            if (cmd_segment.segment_type == SegmentType.env_variable):
                if (link.index < removed_index):
                    setattr(link, '_index', link.index + 1)
            else:
                if (link.index > removed_index):
                    setattr(link, '_index', link.index - 1)
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
            'hostname': self.host,
            'pid': self.pid,
            'status': self.status.name,
            'command': self.actual_command,
            'spawnsAt': DateUtils.try_parse_datetime(self._spawns_at),
            'terminatesAt': DateUtils.try_parse_datetime(self._terminates_at)
         }