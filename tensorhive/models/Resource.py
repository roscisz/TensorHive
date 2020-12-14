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
    __public__ = ['id', 'name', 'hostname']

    id = Column(String(64), primary_key=True)
    name = Column(String(40), nullable=True)
    hostname = Column(String(64), nullable=True)

    _restrictions = relationship('Restriction', secondary='restriction2resource', back_populates='_resources',
                                 viewonly=True)

    def __repr__(self):
        return '<Resource id={id}, name={name}>'.format(id=self.id, name=self.name)

    def check_assertions(self):
        pass

    def get_restrictions(self, include_expired=False, include_global=True):
        """
        :param include_expired: If set to true will also return restrictions that have already expired.
        :param include_global: If set to true will also include global restrictions (which apply to all resources)
        :return: Restrictions assigned to given resource.
        """
        from tensorhive.models.Restriction import Restriction

        restrictions = super(Resource, self).get_restrictions(include_expired)
        if include_global:
            restrictions = list(set(restrictions + Restriction
                                    .get_global_restrictions(include_expired=include_expired)))
        return restrictions

    def get_active_restrictions(self, include_global=True):
        """
        :param include_global: If set to true will also include global restrictions (which apply to all resources)
        :return: Active restrictions (according to start/end times and schedules) assigned to given entity.
        """
        from tensorhive.models.Restriction import Restriction

        restrictions = super(Resource, self).get_active_restrictions()
        if include_global:
            restrictions = list(set(restrictions + Restriction.get_global_restrictions(include_expired=False)))
        return restrictions

    @classmethod
    def get_by_name(cls, resource_name):
        return db_session.query(Resource).filter(Resource.name == resource_name).all()

    @classmethod
    def get_by_hostname(cls, hostname):
        return db_session.query(Resource).filter(Resource.hostname == hostname).all()
