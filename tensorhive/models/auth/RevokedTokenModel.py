from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import Base, db_session


class RevokedTokenModel(Base):
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(120), nullable=False)

    def __repr__(self):
        return '<RevokedToken: id={self.jti}, jti={self.jti}>'

    def save_to_db(self):
        try:
            db_session.add(self)
            db_session.commit()
        #FIXME SQLAlchemyError is a base class for all other, handle all errors in some way
        except IntegrityError:
            db_session.rollback()
            raise

    @classmethod
    def return_all(cls):
        return RevokedTokenModel.query.all()


    def add(self):
        db_session.add(self)
        db_session.comit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)

