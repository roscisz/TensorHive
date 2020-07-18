from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from tensorhive.database import db_session
from tensorhive.models.CRUDModel import CRUDModel
from tensorhive.models.RestrictionAssignee import RestrictionAssignee


class Resource(CRUDModel, RestrictionAssignee):  # type: ignore
    """
    Class representing physical resources (GPUs). id is unique among all resources - GPU's GUID is used. name is
    a custom user-friendly name that may be specified to improve legibility.
    """
    __tablename__ = 'resources'
    id = Column(String(64), primary_key=True)
    name = Column(String(40), nullable=True)

    _restrictions = relationship('Restriction', secondary='restriction2resource')

    def __repr__(self):
        return '<Resource id={id}, name={name}>'.format(id=self.id, name=self.name)

    def check_assertions(self):
        pass

    @classmethod
    def get_by_name(cls, resource_name):
        return db_session.query(Resource).filter(Resource.name == resource_name).all()

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
