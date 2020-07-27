from tensorhive.database import Base


class RestrictionAssignee(Base):  # type: ignore
    """
    Helper base class that should be extended by all entities that are able to be assigned restriction to.
    Currently, such entities are: User, Group and Resource.
    """
    __abstract__ = True

    @property
    def _restrictions(self):
        raise NotImplementedError

    def get_restrictions(self, include_expired=False, include_global=False):
        """
        :param include_expired: If set to true will also return restrictions that have already expired.
        :param include_global: If set to true will also include global restrictions (which apply to all resources)
        :return: Restrictions assigned to given entity.
        """
        from tensorhive.models.Restriction import Restriction

        if include_expired:
            restrictions = self._restrictions
        else:
            restrictions = [r for r in self._restrictions if not r.is_expired]

        if include_global:
            restrictions = list(set(restrictions + Restriction
                                    .get_global_restrictions(include_expired=include_expired)))
        return restrictions

    def get_active_restrictions(self, include_global=False):
        """
        :param include_global: If set to true will also include global restrictions (which apply to all resources)
        :return: Active restrictions (according to start/end times and schedules) assigned to given entity.
        """
        from tensorhive.models.Restriction import Restriction

        restrictions = [r for r in self._restrictions if r.is_active]
        if include_global:
            restrictions = list(set(restrictions + Restriction.get_global_restrictions(include_expired=False)))
        return restrictions
