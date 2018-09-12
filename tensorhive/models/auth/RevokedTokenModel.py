from sqlalchemy import Column,String,Integer
from sqlalchemy.exc import IntegrityError
from tensorhive.database import Base,db_session

class RevokedTokenModel(Base):
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Unique token identifier
    jti = Column(String(120))

    def __repr__(self):
        return '<RevokedToken: id={self.jti}, jti={self.jti}>'

    def save_to_db(self):
        try:
            db_session.add(self)
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
            raise

    def add(self):
        db_session.add(self)
        db_session.comit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)