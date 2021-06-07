from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from tensorhive.database import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.CommandSegment import SegmentType, CommandSegment, CommandSegment2Task
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
    __table_args__ = {'sqlite_autoincrement': True}
    __public__ = ['id', 'job_id', 'hostname', 'pid', 'command']

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'))
    job = relationship("Job", back_populates="_tasks")
    hostname = Column(String(40), nullable=False)
    pid = Column(Integer)
    _status = Column(Enum(TaskStatus), default=TaskStatus.not_running, nullable=False)
    command = Column(String(400), nullable=False)
    _cmd_segments = relationship('CommandSegment', secondary='cmd_segment2task', back_populates='_tasks')
    gpu_id = Column(Integer, nullable=True)  # TODO: link with hardware DB model when it's ready

    def __repr__(self):
        return '<Task id={id}, jobId={job_id}, name={hostname}, command={command}\n' \
            '\tpid={pid}, status={status}>'.format(
                id=self.id,
                job_id=self.job_id,
                hostname=self.hostname,
                command=self.command,
                pid=self.pid,
                status=self._status.name)

    def check_assertions(self):
        pass

    @hybrid_property
    def status(self):
        return self._status

    @status.setter  # type: ignore
    def status(self, value):
        self._status = value
        if self.job is not None:
            self.job.synchronize_status()

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
    def full_command(self):
        _full_command = ''
        start = - self.number_of_env_vars
        end = self.number_of_params + 1
        for i in range(start, 0):
            link = CommandSegment2Task.query.filter(CommandSegment2Task.index == (start - i - 1),
                                                    CommandSegment2Task.task_id == self.id).one()
            cmd_segment = CommandSegment.query.filter(CommandSegment.id == link.cmd_segment_id).one()
            _full_command += cmd_segment.name + '=' + link.value + ' '
        _full_command += self.command + ' '
        for i in range(1, end):
            link = CommandSegment2Task.query.filter(CommandSegment2Task.index == i,
                                                    CommandSegment2Task.task_id == self.id).one()
            cmd_segment = CommandSegment.query.filter(CommandSegment.id == link.cmd_segment_id).one()
            if link.value == '':
                _full_command += cmd_segment.name
            else:
                _full_command += cmd_segment.name + ' ' + link.value
            _full_command += ' '
        _full_command = _full_command[:-1]
        return _full_command

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
        setattr(link, '_value', value)

    def remove_cmd_segment(self, cmd_segment: CommandSegment):
        if cmd_segment not in self.cmd_segments:
            raise Exception('Segment {cmd_segment} is not assigned to task {task}!'
                            .format(cmd_segment=cmd_segment, task=self))
        link = self.get_cmd_segment_link(cmd_segment)
        removed_index = link.index
        self.cmd_segments.remove(cmd_segment)

        for segment in self.cmd_segments:
            link = self.get_cmd_segment_link(segment)
            if (cmd_segment.segment_type == SegmentType.env_variable):
                if (link.index < removed_index):
                    setattr(link, '_index', link.index + 1)
            else:
                if (link.index > removed_index):
                    setattr(link, '_index', link.index - 1)
        self.save()

    def as_dict(self, include_private=None):
        ret = super(Task, self).as_dict(include_private=include_private)
        ret['status'] = self._status.name
        try:
            envs_array = []
            params_array = []
            for cmd_segment in self.cmd_segments:
                link = self.get_cmd_segment_link(cmd_segment)
                segment = {
                    'name': cmd_segment.name,
                    'value': link.value,
                    'index': link.index
                }
                if cmd_segment.segment_type == SegmentType.env_variable:
                    envs_array.append(segment)
                elif cmd_segment.segment_type == SegmentType.parameter:
                    params_array.append(segment)
            ret['cmdsegments'] = {
                'envs': envs_array,
                'params': params_array
            }
        except Exception:
            ret['cmdsegments'] = []
        finally:
            return ret
