from tensorhive.database import db_session
from sqlalchemy import Column,String,Integer

class RevokedTokenModel():
    __tablename__ = 'revoked_tokens'
    id =  Column(Integer, primary_key=True)
    # Unique token identifier
    jti = Column(String(120))

    def add(self):
        db_session.add(self)
        db_session.comit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)