from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, and_, not_, or_, event
from tensorhive.database import db_session, Base
from tensorhive.models.CRUDModel import CRUDModel
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from typing import Optional, List
import datetime
import logging
log = logging.getLogger(__name__)


class Reservation(CRUDModel, Base):  # type: ignore
    __tablename__ = 'reservations'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    # TODO 'owner' would be much better name (needs refactoring)
    user = relationship(
        'User',
        backref=backref('reservations', passive_deletes=True, cascade='all, delete, delete-orphan'),
        lazy='subquery')
    title = Column(String(60), unique=False, nullable=False)
    description = Column(String(200), nullable=True)
    protected_resource_id = Column(String(60), nullable=False)

    gpu_util_avg = Column(Integer, nullable=True)
    mem_util_avg = Column(Integer, nullable=True)

    # Stored as UTC time
    _starts_at = Column(DateTime, nullable=False)
    _ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __min_reservation_time = datetime.timedelta(minutes=30)
    __max_reservation_time = datetime.timedelta(days=8)

    def check_assertions(self):
        assert self.user_id, 'Reservation owner must be given!'
        assert self.protected_resource_id, 'Reservation must be related with a resource!'
        assert self.starts_at, 'Reservation start time is invalid!'
        assert self.ends_at, 'Reservation end time is invalid!'
        assert self.duration >= self.__min_reservation_time, 'Reservation duration is too short!'
        assert self.duration <= self.__max_reservation_time, 'Reservation duration is too long!'

        assert 0 < len(self.title) < 60, 'Reservation title length has incorrect length!'
        assert len(self.description) < 200, 'Reservation description has incorrect length!'
        assert len(self.protected_resource_id) == 40, 'Protected resource UUID has incorrect length!'

        collision = self.would_interfere()
        assert not collision, 'Reservation would interfere with some other reservation!'

    @hybrid_property
    def duration(self):
        return self.ends_at - self.starts_at

    @classmethod
    def parsed_input_datetime(cls, value: str) -> Optional[datetime.datetime]:
        client_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        try:
            result = datetime.datetime.strptime(value, client_datetime_format)
        except ValueError as e:
            log.error(e)
            raise
        else:
            return result

    @classmethod
    def parsed_output_datetime(cls, value: datetime.datetime) -> str:
        display_datetime_format = '%Y-%m-%dT%H:%M:%S'
        server_timezone = '+00:00'
        return value.strftime(display_datetime_format) + server_timezone

    @hybrid_property
    def starts_at(self):
        return self._starts_at

    @starts_at.setter  # type: ignore
    def starts_at(self, value):
        if isinstance(value, str):
            self._starts_at = self.parsed_input_datetime(value)
        elif isinstance(value, datetime.datetime):
            self._starts_at = value
        else:
            self._starts_at = None
            log.error('Unsupported type (starts_at={})'.format(value))

    @hybrid_property
    def ends_at(self):
        return self._ends_at

    @ends_at.setter  # type: ignore
    def ends_at(self, value):
        if isinstance(value, str):
            try:
                self._ends_at = Reservation.parsed_input_datetime(value)
            except ValueError:
                # Catch, but don't propagate at this moment,
                # let the dev to change it to correct value later
                self._ends_at = None
        elif isinstance(value, datetime.datetime):
            self._ends_at = value
        else:
            self._ends_at = None
            log.error('Unsupported type (ends_at={})'.format(value))

    @classmethod
    def current_events(cls):
        '''Returns only those events that should be currently respected by users'''
        current_time = datetime.datetime.utcnow()
        return cls.query.filter(
            and_(
                # Events that has already started
                cls.starts_at <= current_time,
                # Events before their end
                current_time <= cls.ends_at)).all()

    def would_interfere(self):
        return Reservation.query.filter(
            # Two events overlap in time domain
            and_(
                self.starts_at < Reservation.ends_at,
                self.ends_at > Reservation.starts_at
            ),
            # Case concerns the same resource
        ).filter(Reservation.id != self.id)\
         .filter(Reservation.protected_resource_id == self.protected_resource_id).first()

    @classmethod
    def filter_by_uuids_and_time_range(cls, uuids: List[str], start: datetime.datetime, end: datetime.datetime):
        '''
        Returns all reservations that overlap with <start, end> in any way:
        X|   X|, |X   X|, |X   |X or |X   X|

        and have UUID matching any of those from specified in uuids
        '''
        assertion_failed_msg = 'Argument must be of type datetime.datetime!'
        assert isinstance(start, datetime.datetime), assertion_failed_msg
        assert isinstance(end, datetime.datetime), assertion_failed_msg

        uuid_filter = cls.protected_resource_id.in_(uuids)
        after_start_filter = cls.starts_at <= end
        before_end_filter = start <= cls.ends_at
        matching_conditions = and_(uuid_filter, after_start_filter, before_end_filter)
        return cls.query.filter(matching_conditions).all()

    def __repr__(self):
        return '''
<ReservationEvent id={0}, user_id={1}
    title={2}
    description={3}
    protected_resource_id={4}

    gpu_util_avg={5}
    mem_util_avg={6}

    starts_at={7}
    ends_at={8}
    created_at={9}'''.format(self.id, self.user_id, self.title, self.description, self.protected_resource_id,
                             self.gpu_util_avg, self.mem_util_avg, self.starts_at, self.ends_at, self.created_at)

    @property
    def as_dict(self):
        '''Serializes model instance into dict (which is interpreted as json automatically)'''
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'resourceId': self.protected_resource_id,
            'userId': self.user_id,
            'userName': self.user.username,
            'gpuUtilAvg': self.gpu_util_avg,
            'memUtilAvg': self.mem_util_avg,
            'start': self.parsed_output_datetime(self.starts_at),
            'end': self.parsed_output_datetime(self.ends_at),
            'createdAt': self.parsed_output_datetime(self.created_at)
        }
