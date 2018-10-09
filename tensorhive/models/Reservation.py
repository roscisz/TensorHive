import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, and_, not_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import validates
from tensorhive.database import db
from tensorhive.models.User import User
from tensorhive.models.CRUDModel import CRUDModel
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
import logging
log = logging.getLogger(__name__)


class Reservation(CRUDModel, db.Model):
    __tablename__ = 'reservation_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(60), unique=False, nullable=False)
    description = Column(String(200), nullable=True)
    protected_resource_id = Column(String(60), nullable=False)

    # Stored as UTC time
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __display_datetime_format = '%Y-%m-%dT%H:%M:%S'
    __server_timezone = '+00:00'
    __min_reservation_time = datetime.timedelta(minutes=30)

    def check_assertions(self):
        assert User.get(self.user_id), 'Reservation owner does not exist!'
        assert self.protected_resource_id, 'Reservation must be related with some resource!'
        assert self.starts_at and self.ends_at, 'Reservation time range is not specified!'
        assert self.duration >= self.__min_reservation_time, 'Reservation duration is too short!'

        assert 8 < len(self.title) < 60, 'Reservation title length has incorrect length!'
        assert 8 < len(self.description) < 200, 'Reservation description has incorrect length!'
        assert len(self.protected_resource_id) == 40, 'Protected resource UUID has incorrect length!'

        #print([m.key for m in Reservation.__table__.columns])
        #collision = self.would_interfere()
        #assert not collision, 'Reservation would interfere with some other reservation!'
        # TODO Check time collisions for the same resource
        # print(obj.title, obj.start, obj.end)
        #[print(a.as_dict) for a in .query.all()]
        # print(len(cls.query.all()))
        # collision = cls.collision_found(obj.start, obj.end, obj.protected_resource_id)
        # print('collision: ', collision)
        # assert not collision, 'Reservation collides with {}'.format(collision)

    @hybrid_property
    def duration(self):
        return self.ends_at - self.starts_at

    def __repr__(self):
        return '''
<ReservationEvent id={0}, user={1}
    title={2}
    description={3}
    protected_resource_id={4}

    starts_at={5}
    ends_at={6}
    created_at={7}'''.format(
            self.id, self.user,
            self.title, self.description,
            self.protected_resource_id,
            self.starts_at, self.ends_at,
            self.created_at)

    # @classmethod
    # def current_events(cls):
    #     '''Returns only those events that should be currently respected by the users'''
    #     current_time = datetime.datetime.utcnow()
    #     return cls.query.filter(and_(cls.starts_at <= current_time, current_time <= cls.ends_at)).all()

    # @validates('starts_at', 'ends_at')
    # def validate_time_range(self, key, field):
    #     '''Parse datetime if it's a string, otherwise do nothing'''
    #     if isinstance(field, str):
    #         client_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    #         try:
    #             field = datetime.datetime.strptime(field, client_datetime_format)
    #         except ValueError:
    #             raise ValueError('Datetime parsing error')
    #     return field

    # # @classmethod
    # def would_interfere(self):
    #     # TODO Double check
    #     return Reservation.query.filter(
    #         # Two events overlap and concern the same resource
    #         and_(
    #             # There are no such two events that overlap
    #             not_(
    #                 # Two events overlap
    #                 or_(self.ends_at < Reservation.starts_at, self.starts_at > Reservation.ends_at)
    #             ),
    #             # Case concerns the same resource
    #             Reservation.protected_resource_id == self.protected_resource_id)
    #         ).first()

    # # def _check_for_collisions(self):
    # #     '''Assures that there are no other reservations for the same resource in that time'''
    # #     if self.collision_found(self.start, self.end, self.protected_resource_id):
    # #         raise AssertionError('{uuid} is already reserved from {start} to {end}'.format(
    # #             uuid=self.resource_id,
    # #             start=self.start,
    # #             end=self.end))

    # # def _parse_client_time_format(self):
    # #     if isinstance(self.start, str) and isinstance(self.start, str): 
    # #         client_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    # #         parsed_datetime = lambda t: datetime.datetime.strptime(t, client_datetime_format)
    # #         try:
    # #             self.start = parsed_datetime(self.start)
    # #             self.end = parsed_datetime(self.end)
    # #         except ValueError:
    # #             raise ValueError('Datetime parsing error')

    # @classmethod
    # def find_by_id(cls, id):
    #     return cls.query.get(id)

    # @classmethod
    # def filter_by_uuids_and_time_range(cls, uuids, start, end):
    #     uuid_filter = cls.protected_resource_id.in_(uuids)
    #     after_start_filter = cls.start <= end
    #     before_end_filter = start <= cls.end
    #     matching_conditions = and_(uuid_filter, after_start_filter, before_end_filter)
    #     return cls.query.filter(matching_conditions).all()

    # # @classmethod
    # # def delete_by_id(cls, id):
    # #     try:
    # #         num_rows_deleted = cls.query.filter_by(id=id).delete()
    # #         db_session.commit()
    # #     except:
    # #         db_session.rollback()
    # #         return False
    # #     # Check if any row were affected by deletion (otherwise -> not found)
    # #     return True if num_rows_deleted > 0 else False

    # @property
    # def as_dict(self):
    #     '''Serializes model instance into dict (which is interpreted as json automatically)'''
    #     return dict(id=self.id,
    #                 title=self.title,
    #                 description=self.description,
    #                 resourceId=self.protected_resource_id,
    #                 userId=self.user_id,
    #                 start=self.start.strftime(
    #                     self.__display_datetime_format)
    #                 + self.__server_timezone,
    #                 end=self.end.strftime(
    #                     self.__display_datetime_format)
    #                 + self.__server_timezone,
    #                 createdAt=self.created_at.strftime(
    #                     self.__display_datetime_format)
    #                 )
