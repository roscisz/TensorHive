from passlib.hash import pbkdf2_sha256 as sha256
import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import Base, db_session


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(40), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User: id={self.id}, username={self.username}, created_at={self.created_at}>'

    # TODO updated_at timestamp, role and more

    def save_to_db(self):
        try:
            db_session.add(self)
            db_session.commit()
        #FIXME SQLAlchemyError is a base class for all other, handle all errors in some way
        except IntegrityError:
            db_session.rollback()
            raise
            

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        return UserModel.query.all()

    @property
    def as_dict(self):
        '''Serializes model instance into dict (which is interpreted as json automatically)'''
        return dict(id=self.id,
                    username=self.username,
                    created_at=self.created_at.isoformat()
                    )
    # TODO We may need deserialzer
    
    # Not implemented yet
    # @classmethod
    # def get_count(cls):
    #     count_q = self.statement.with_only_columns([func.count()]).order_by(None)
    #     count = q.session.execute(count_q).scalar()
    #     return count

    #     users_list = list(map(lambda user: as_json(user), all_users))
    #     return {'users': users_list}

    # @classmethod
    # def delete_all(cls):
    #     try:
    #         num_rows_deleted = db.session.query(cls).delete()
    #         db.session.commit()
    #         return {'message': '{} user(s) deleted'.format(num_rows_deleted)}
    #     except:
    #         return {'message': 'Deleting all users operation failed'}

    # @staticmethod
    # def generate_hash(password):
    #     return sha256.hash(password)

    # @staticmethod
    # def verify_hash(password, hash):
    #     return sha256.verify(password, hash)
