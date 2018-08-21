import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import Base, db_session


class ReservationEventModel(Base):
    __tablename__ = 'reservation_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(60), unique=False, nullable=False)
    description = Column(String(200), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    resource_id = Column(String(60), nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # TODO Relation with user

    __display_datetime_format = '%Y-%m-%dT%H:%M:%S'
    __server_timezone = '+00:00'

    def __repr__(self):
        return '<ReservationEvent: id={id}, \n \
                title={title}, \n \
                resource_id={resource_id}, \n \
                user_id={user_id}, \n \
                description={description}, \n \
                created_at={created_at}>'.format(id=self.id,
                                                 title=self.title,
                                                 resource_id=self.resource_id,
                                                 user_id=self.user_id,
                                                 description=self.description,
                                                 created_at=self.created_at)

    @classmethod
    def find_resource_events_between(cls, start, end, resource_id):
        return cls.query.filter(and_(cls.start >= start, cls.end <= end, cls.resource_id == resource_id)).first()

    @classmethod
    def current_events(cls):
        '''Returns only those events that should be currently respected by the users'''
        current_time = datetime.datetime.utcnow()
        return cls.query.filter(and_(cls.start <= current_time, current_time <= cls.end)).all()

    def save_to_db(self):
        try:
            db_session.add(self)
            db_session.commit()
        except:
            db_session.rollback()
            return False
        return True

    @classmethod
    def find_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def return_all(cls):
        return cls.query.all()

    @classmethod
    def return_selected(cls, resources_ids, start, end):
        return cls.query.filter(and_(cls.resource_id.in_(resources_ids), cls.start<=end, cls.end>=start)).all()

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
                        +self.__server_timezone,
                    end=self.end.strftime(
                        self.__display_datetime_format)
                        +self.__server_timezone,
                    createdAt=self.created_at.strftime(
                        self.__display_datetime_format)
                    )
    # TODO We may need deserialzer

    # Not implemented yet
    # @classmethod
    # def get_count(cls):
    #     pass
