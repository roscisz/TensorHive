from sqlalchemy import Column, Integer, String, ForeignKey
#from sqlalchemy.exc import SQLAlchemyError
from tensorhive.database import Base
from tensorhive.models.CRUDModel import CRUDModel
import logging
log = logging.getLogger(__name__)


class Task(CRUDModel, Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    host = Column(String(40), nullable=False)
    pid = Column(Integer, nullable=True)
    exit_code = Column(Integer, nullable=True)
    command = Column(String(400), nullable=False)

    def __repr__(self):
        return '<Task id={id}, user={user}, hostname={hostname}, command={command}\n' \
            '\tpid={pid}, exit_code={exit_code}>'.format(
            id=self.id,
            user=self.user,
            hostname=self.host,
            command=self.command,
            pid=self.pid,
            exit_code=self.exit_code)

    def check_assertions(self):
        pass

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'hostname': self.host,
            'pid': self.pid,
            'exit_code': self.exit_code,
            'command': self.command
        }