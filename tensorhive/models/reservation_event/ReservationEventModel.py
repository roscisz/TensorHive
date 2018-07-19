import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import Base, db_session


class ReservationEventModel(Base):
    __tablename__ = 'reservation_events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(60), unique=False, nullable=False)
    description = Column(String(200), nullable=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    # TODO Relation with user

    __display_datetime_format = '%Y-%m-%dT%H:%M:%S'

    def __repr__(self):
        return '<ReservationEvent: id={id}, \n \
                title={title}, \n \
                description={description}, \n \
                created_at={created_at}>'.format(id=self.id, title=self.title, description=self.description, created_at=self.created_at)

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
                    start=self.start.strftime(
                        self.__display_datetime_format),
                    end=self.end.strftime(
                        self.__display_datetime_format),
                    created_at=self.created_at.strftime(
                        self.__display_datetime_format)
                    )
    # TODO We may need deserialzer

    # Not implemented yet
    # @classmethod
    # def get_count(cls):
    #     pass