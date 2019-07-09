from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from datetime import datetime
from tensorhive.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from tensorhive.models.CRUDModel import CRUDModel
from typing import Optional, Union
import enum
import logging
log = logging.getLogger(__name__)


# FIXME Move to utils
def parsed_input_datetime(value: str) -> datetime:
    """Tries to parse string into datetime.

    Re-raises ValueError on failure
    """
    client_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    try:
        result = datetime.strptime(value, client_datetime_format)
    except ValueError:
        log.warning('Could not parse input into datetime')
        raise
    else:
        return result


# FIXME Move to utils
def try_parse_input_datetime(value: Union[str, datetime, None]) -> Optional[datetime]:
    """Allows for string to datetime conversion given in API request.
    If new value is of `datetime` type then it just returns original value as it is.

    Re-rasies ValueError
    """
    if isinstance(value, str):
        return parsed_input_datetime(value)
    elif isinstance(value, datetime):
        return value
    else:
        return None


class TaskStatus(enum.Enum):
    not_running = 1
    running = 2
    terminated = 3
    unsynchronized = 4


class Task(CRUDModel, Base):  # type: ignore
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship(
        'User', backref=backref('tasks', passive_deletes=True, cascade='all, delete, delete-orphan'), lazy='subquery')
    host = Column(String(40), nullable=False)
    pid = Column(Integer, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.not_running, nullable=False)
    command = Column(String(400), nullable=False)
    spawn_at = Column(DateTime, nullable=True)
    terminate_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return '<Task id={id}, user={user}, name={host}, command={command}\n' \
            '\tpid={pid}, status={status}, spawn_at={spawn_at}, terminate_at={terminate_at}>'.format(
                id=self.id,
                user=self.user,
                host=self.host,
                command=self.command,
                pid=self.pid,
                status=self.status.name,
                spawn_at=self.spawn_at,
                terminate_at=self.terminate_at)

    def check_assertions(self):
        pass

    # FIXME Code copied from `Reservation.py` and adapted to Optional[datetime] use case (refactor in both places)
    @classmethod
    def try_parse_output_datetime(cls, value: Optional[datetime]) -> Optional[str]:
        """Parses datetime object taking timezone postfix into consideration.
        Note that `spawn_at`, `terminate_at` are nullable fields, hence None can be returned.
        """
        if not value:
            return None
        display_datetime_format = '%Y-%m-%dT%H:%M:%S'
        server_timezone = '+00:00'
        return value.strftime(display_datetime_format) + server_timezone

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'hostname': self.host,
            'pid': self.pid,
            'status': self.status.name,
            'command': self.command,
            'spawnAt': self.try_parse_output_datetime(self.spawn_at),
            'terminateAt': self.try_parse_output_datetime(self.terminate_at)
        }
