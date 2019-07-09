from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from tensorhive.database import db_session, Base
from tensorhive.models.CRUDModel import CRUDModel
import logging
log = logging.getLogger(__name__)


class RevokedToken(CRUDModel, Base):  # type: ignore
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(120), unique=True, nullable=False)

    def check_assertions(self):
        pass

    def __repr__(self):
        return '<RevokedToken: id={id}, jti={jti}>'.format(
            id=self.id,
            jti=self.jti)

    @classmethod
    def is_jti_blacklisted(cls, jti):
        # with flask_app.app_context():
        return bool(cls.query.filter_by(jti=jti).first())
