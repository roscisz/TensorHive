from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import Base, db_session
from tensorhive.models.CRUDModel import CRUDModel
import logging
log = logging.getLogger(__name__)

class RevokedToken(CRUDModel, Base):
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(120), unique=True, nullable=False)


    def __repr__(self):
        return '<RevokedToken: id={id}, jti={jti}>'.format(
            id=self.id,
            jti=self.jti)

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
