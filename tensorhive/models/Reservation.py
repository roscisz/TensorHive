from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, and_, not_, or_, event
from tensorhive.database import db_session, Base
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.utils.DateUtils import DateUtils
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from typing import List
import datetime
import logging
log = logging.getLogger(__name__)


class Reservation(CRUDModel, Base):  # type: ignore
    __tablename__ = 'reservations'
    __table_args__ = {'sqlite_autoincrement': True}
    __public__ = ['id', 'title', 'description', 'resource_id', 'user_id', 'gpu_util_avg', 'mem_util_avg', 'start',
                  'end', 'created_at', 'is_cancelled']

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship(
        'User',
        backref=backref('reservations', passive_deletes=True, cascade='all, delete, delete-orphan'),
        lazy='subquery')
    title = Column(String(60), unique=False, nullable=False)
    description = Column(String(200), nullable=True)
    resource_id = Column(String(60), nullable=False)
    _is_cancelled = Column('is_cancelled', Boolean, nullable=True)

    gpu_util_avg = Column(Integer, nullable=True)
    mem_util_avg = Column(Integer, nullable=True)

    # Stored as UTC time
    _start = Column(DateTime, nullable=False)
    _end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __min_reservation_time = datetime.timedelta(minutes=30)
    __max_reservation_time = datetime.timedelta(days=8)

    def check_assertions(self):
        assert self.user_id, 'Reservation owner must be given!'
        assert self.resource_id, 'Reservation must be related with a resource!'
        assert self.start, 'Reservation start time is invalid!'
        assert self.end, 'Reservation end time is invalid!'
        assert self.duration >= self.__min_reservation_time, 'Reservation duration is too short!'
        assert self.duration <= self.__max_reservation_time, 'Reservation duration is too long!'

        assert 0 < len(self.title) < 60, 'Reservation title length has incorrect length!'
        assert len(self.description) < 200, 'Reservation description has incorrect length!'
        assert len(self.resource_id) == 40, 'Protected resource UUID has incorrect length!'

        collision = self.would_interfere()
        assert not collision, 'Reservation would interfere with some other reservation!'

    @hybrid_property
    def duration(self):
        return self.end - self.start

    @hybrid_property
    def start(self):
        return self._start

    @start.setter  # type: ignore
    def start(self, value):
        self._start = DateUtils.try_parse_string(value)
        if self._start is None:
            log.error('Unsupported type (start={})'.format(value))

    @hybrid_property
    def end(self):
        return self._end

    @end.setter  # type: ignore
    def end(self, value):
        self._end = DateUtils.try_parse_string(value)
        if self._end is None:
            log.error('Unsupported type (end={})'.format(value))

    @hybrid_property
    def is_cancelled(self):
        return self._is_cancelled is not None and self._is_cancelled

    @is_cancelled.setter  # type: ignore
    def is_cancelled(self, value):
        self._is_cancelled = value

    @classmethod
    def current_events(cls):
        '''Returns only those events that should be currently respected by users'''
        current_time = datetime.datetime.utcnow()
        current_events = cls.query.filter(
            and_(
                # Events that has already started
                cls.start <= current_time,
                # Events before their end
                current_time <= cls.end)).all()
        return [c for c in current_events if not c.is_cancelled]

    def would_interfere(self):
        conflicting_reservations = Reservation.query.filter(
            # Two events overlap in time domain
            and_(
                self.start < Reservation.end,
                self.end > Reservation.start
            ),
            # Case concerns the same resource
        ).filter(Reservation.id != self.id)\
         .filter(Reservation.resource_id == self.resource_id).all()
        return any(not r.is_cancelled for r in conflicting_reservations)

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

        uuid_filter = cls.resource_id.in_(uuids)
        after_start_filter = cls.start <= end  # type: ignore
        before_end_filter = start <= cls.end  # type: ignore
        matching_conditions = and_(uuid_filter, after_start_filter, before_end_filter)
        return cls.query.filter(matching_conditions).all()

    def __repr__(self):
        return '''
<ReservationEvent id={0}, user_id={1}
    title={2}
    description={3}
    resource_id={4}

    gpu_util_avg={5}
    mem_util_avg={6}

    start={7}
    end={8}
    created_at={9}'''.format(self.id, self.user_id, self.title, self.description, self.resource_id,
                             self.gpu_util_avg, self.mem_util_avg, self.start, self.end, self.created_at)

    def as_dict(self, include_private=False):
        ret = super(Reservation, self).as_dict(include_private=include_private)
        ret['userName'] = self.user.username
        return ret
