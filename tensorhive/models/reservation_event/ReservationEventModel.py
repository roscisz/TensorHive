import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, and_, not_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import validates
from tensorhive.database import Base, db_session
from tensorhive.models.user.UserModel import UserModel
import logging
log = logging.getLogger(__name__)


class ReservationEventModel(Base):
    __tablename__ = 'reservation_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(60), unique=False, nullable=False)
    description = Column(String(200), nullable=True)
    resource_id = Column(String(60), nullable=False)

    # Stored as UTC time
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __display_datetime_format = '%Y-%m-%dT%H:%M:%S'
    __server_timezone = '+00:00'
    __min_reservation_time = datetime.timedelta(minutes=30)

    def __repr__(self):
        return '<ReservationEvent id={id}, user={user}, \n \
                title={title}, \n \
                description={description}, \n \
                resource_id={resource_id}, \n \
                start={start}, \n \
                end={end}, \n \
                created_at={created_at}>'.format(id=self.id,
                                                 title=self.title,
                                                 resource_id=self.resource_id,
                                                 user=self.user,
                                                 description=self.description,
                                                 created_at=self.created_at,
                                                 start=self.start,
                                                 end=self.end)


    @classmethod
    def current_events(cls):
        '''Returns only those events that should be currently respected by the users'''
        current_time = datetime.datetime.utcnow()
        return cls.query.filter(and_(cls.start <= current_time, current_time <= cls.end)).all()

    def save_to_db(self):
        try:
            self._parse_client_time_format()
            self._validate_user_existence()
            self._validate_time_range()
            self._check_for_collisions()

            db_session.add(self)
            db_session.commit()
            log.debug('Created {}'.format(self))
        except IntegrityError as e:
            db_session.rollback()
            log.error(e.__cause__)
            return False
        except (AssertionError, TypeError, ValueError) as e:
            log.error(e)
            return False
        return True

    def _validate_user_existence(self):
        if not UserModel.find_by_id(self.user_id):
            raise AssertionError(
                'User with id={} does not exist'.format(self.user_id))

    def _validate_time_range(self):
        if not isinstance(self.start, datetime.date) or not isinstance(self.end, datetime.date):
            raise TypeError(
                '\'start\' and \'end\' must be of type datetime.datetime')

        if self.start > self.end:
            raise AssertionError('Invalid time range (start >= end)')

        if self.start + self.__min_reservation_time > self.end:
            raise AssertionError('Reservation time is shorter than {}'.format(
                self.__min_reservation_time))

    @classmethod
    def collision_found(cls, start, end, resource_id):
        return cls.query.filter(
            # Two events overlap and concern the same resource
            and_(
                # There are no such two events that overlap
                not_(
                    # Two events overlap
                    or_(end < cls.start, start > cls.end)
                ), 
                # Case concerns the same resource
                cls.resource_id == resource_id)
            ).first()

    def _check_for_collisions(self):
        '''Assures that there are no other reservations for the same resource in that time'''
        if self.collision_found(self.start, self.end, self.resource_id):
            raise AssertionError('{uuid} is already reserved from {start} to {end}'.format(
                uuid=self.resource_id,
                start=self.start,
                end=self.end))

    def _parse_client_time_format(self):
        if isinstance(self.start, str) and isinstance(self.start, str): 
            client_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
            parsed_datetime = lambda t: datetime.datetime.strptime(t, client_datetime_format)
            try:
                self.start = parsed_datetime(self.start)
                self.end = parsed_datetime(self.end)
            except ValueError:
                raise ValueError('Datetime parsing error')

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def return_all(cls):
        return cls.query.all()

    @classmethod
    def filter_by_uuids_and_time_range(cls, uuids, start, end):
        match_uuids = cls.resource_id.in_(uuids)
        match_after_start = cls.start <= end
        match_before_end = start <= cls.end
        return cls.query.filter(and_(match_uuids, match_after_start, match_before_end)).all()

    @classmethod
    def delete_by_id(cls, id):
        try:
            num_rows_deleted = cls.query.filter_by(id=id).delete()
            db_session.commit()
        except:
            db_session.rollback()
            return False
        # Check if any row were affected by deletion (otherwise -> not found)
        return True if num_rows_deleted > 0 else False

    @property
    def as_dict(self):
        '''Serializes model instance into dict (which is interpreted as json automatically)'''
        return dict(id=self.id,
                    title=self.title,
                    description=self.description,
                    resourceId=self.resource_id,
                    userId=self.user_id,
                    start=self.start.strftime(
                        self.__display_datetime_format)
                    + self.__server_timezone,
                    end=self.end.strftime(
                        self.__display_datetime_format)
                    + self.__server_timezone,
                    createdAt=self.created_at.strftime(
                        self.__display_datetime_format)
                    )
    # TODO We may need deserialzer

    # Not implemented yet
    # @classmethod
    # def get_count(cls):
    #     pass
