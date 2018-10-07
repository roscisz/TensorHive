import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, and_, not_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import validates
from tensorhive.database import Base, db_session
from tensorhive.models.User import User
from tensorhive.models.CRUDModel import CRUDModel
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
import logging
log = logging.getLogger(__name__)


class Reservation(CRUDModel, Base):
    __tablename__ = 'reservation_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
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

    @classmethod
    def validate_columns(cls, new_object):
        if new_object.title == 'asd':
            raise AssertionError('Validate coumns example error')

    @hybrid_property
    def duration(self):
        return self.end - self.start

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
            User.get(self.user_id)
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
        except (NoResultFound, MultipleResultsFound) as e:
            log.error(e)
            raise AssertionError('Reservation has no user assigned!')
            return False
        return True

    @validates('resource_id')
    def validate_resource(self, key, field):
        if not isinstance(field, str):
            raise AssertionError('Resource ID is not a string')

        if len(field) < 4:
            # TODO More realistic validation
            raise AssertionError('Resource ID is too short')

        return field

    @validates('start', 'end')
    def validate_time_range(self, key, field):
        # Parse datetime if it's a string
        if isinstance(field, str):
            client_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
            try:
                field = datetime.datetime.strptime(field, client_datetime_format)
            except ValueError:
                raise ValueError('Datetime parsing error')

        # Check constraints
        time_constraint_msg = 'Reservation must start before it ends. ' \
            'Min. duration = {}'.format(self.__min_reservation_time)

        time_collision_msg = '{uuid} is already reserved from {start} to {end}'.format(
            uuid=self.resource_id,
            start=self.start,
            end=self.end
        )

        if key == 'end' and isinstance(self.start, datetime.datetime):
            if self.start + self.__min_reservation_time > field:
                raise AssertionError(time_constraint_msg)
        elif key == 'start' and isinstance(self.end, datetime.datetime):
            if field + self.__min_reservation_time > self.end:
                raise AssertionError(time_constraint_msg)
            #if self.collision_found(field, self.end, )    
        
        return field

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

    # def _parse_client_time_format(self):
    #     if isinstance(self.start, str) and isinstance(self.start, str): 
    #         client_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    #         parsed_datetime = lambda t: datetime.datetime.strptime(t, client_datetime_format)
    #         try:
    #             self.start = parsed_datetime(self.start)
    #             self.end = parsed_datetime(self.end)
    #         except ValueError:
    #             raise ValueError('Datetime parsing error')

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def filter_by_uuids_and_time_range(cls, uuids, start, end):
        uuid_filter = cls.resource_id.in_(uuids)
        after_start_filter = cls.start <= end
        before_end_filter = start <= cls.end
        matching_conditions = and_(uuid_filter, after_start_filter, before_end_filter)
        return cls.query.filter(matching_conditions).all()

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
