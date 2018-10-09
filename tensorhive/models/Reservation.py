import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, and_, not_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import validates
from tensorhive.database import db, flask_app
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
        assert self.user_id, 'Reservation owner must be given!'
        assert self.protected_resource_id, 'Reservation must be related with a resource!'
        assert self.starts_at and self.ends_at, 'Reservation time range is not specified!'
        assert self.duration >= self.__min_reservation_time, 'Reservation duration is too short!'

        assert 8 < len(self.title) < 60, 'Reservation title length has incorrect length!'
        assert 8 < len(self.description) < 200, 'Reservation description has incorrect length!'
        assert len(self.protected_resource_id) == 40, 'Protected resource UUID has incorrect length!'

        collision = self.would_interfere()
        assert not collision, 'Reservation would interfere with some other reservation!'


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

    @classmethod
    def current_events(cls):
        '''Returns only those events that should be currently respected by users'''
        current_time = datetime.datetime.utcnow()
        with flask_app.app_context():
            return cls.query.filter(
                and_(
                    # Events that has already started
                    cls.starts_at <= current_time, 
                    # Events before their end 
                    current_time <= cls.ends_at)
                ).all()

    def would_interfere(self):
        return Reservation.query.filter(
                # Two events overlap in time domain
                and_(
                    self.starts_at <= Reservation.ends_at,
                    self.ends_at >= Reservation.starts_at
                ),
                # Case concerns the same resource
                Reservation.protected_resource_id == self.protected_resource_id
            ).first()



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
