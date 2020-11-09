import logging
from http import HTTPStatus
from typing import Any, Dict, List, Optional, Tuple, Union
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.authorization import admin_required
from tensorhive.config import API
from tensorhive.core.utils.ReservationVerifier import ReservationVerifier
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from tensorhive.models.Group import Group
from tensorhive.models.Resource import Resource
from tensorhive.models.Restriction import Restriction
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from tensorhive.models.User import User
from tensorhive.utils.DateUtils import DateUtils
from stringcase import snakecase

log = logging.getLogger(__name__)
RESTRICTION = API.RESPONSES['restriction']
USER = API.RESPONSES['user']
GROUP = API.RESPONSES['group']
RESOURCE = API.RESPONSES['resource']
NODES = API.RESPONSES['nodes']
SCHEDULE = API.RESPONSES['schedule']
GENERAL = API.RESPONSES['general']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
RestrictionId = int
UserId = int
GroupId = int
ResourceId = str
ScheduleId = int


def get_all() -> Tuple[List[Any], HttpStatusCode]:
    return [
        restriction.as_dict(include_groups=True, include_users=True,
                            include_resources=True) for restriction in Restriction.all()
    ], HTTPStatus.OK.value


def get_selected(user_id: Optional[UserId], group_id: Optional[GroupId], resource_id: Optional[ResourceId],
                 schedule_id: Optional[ScheduleId], include_user_groups: Optional[bool] = False) \
        -> Tuple[Union[List[Any], Content], HttpStatusCode]:
    try:
        # If a specific group is selected then groups are not included in the restriction information in response
        # The same applies to users and resources
        include_groups = group_id is None
        include_users = user_id is None
        include_resources = schedule_id is None

        restrictions = []  # type: List[Restriction]
        if user_id is not None:
            user = User.get(user_id)
            restrictions.extend(user.get_restrictions(include_group=include_user_groups))
        if group_id is not None:
            group = Group.get(group_id)
            restrictions.extend(group.get_restrictions())
        if resource_id is not None:
            resource = Resource.get(resource_id)
            restrictions.extend(resource.get_restrictions())
        if schedule_id is not None:
            schedule = RestrictionSchedule.get(schedule_id)
            restrictions.extend(schedule.restrictions)

        # Take unique restrictions
        result = set(restrictions)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': GENERAL['bad_request']}, HTTPStatus.BAD_REQUEST.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content = [restriction.as_dict(include_groups=include_groups, include_users=include_users,  # type: ignore
                                       include_resources=include_resources) for restriction in result]
        status = HTTPStatus.OK.value
    finally:
        return content, status


@jwt_required
def get(user_id: Optional[UserId] = None, group_id: Optional[GroupId] = None, resource_id: Optional[ResourceId] = None,
        schedule_id: Optional[ScheduleId] = None, include_user_groups: Optional[bool] = False) \
        -> Tuple[Union[List[Any], Content], HttpStatusCode]:
    args = [user_id, include_user_groups, group_id, resource_id, schedule_id]
    all_args_none = all(a is None for a in args)

    if all_args_none:
        return get_all()
    else:
        # Filter restrictions
        return get_selected(user_id, group_id, resource_id, schedule_id, include_user_groups)


@admin_required
def create(restriction: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        new_restriction = Restriction(
            name=restriction.get('name'),
            starts_at=restriction['startsAt'],
            is_global=restriction['isGlobal'],
            ends_at=DateUtils.try_parse_string(restriction.get('endsAt'))
        )
        new_restriction.save()
    except AssertionError as e:
        content = {'msg': RESTRICTION['create']['failure']['invalid'].format(reason=e)}
        status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        content = {'msg': GENERAL['internal_error'] + str(e)}
        status = HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content = {
            'msg': RESTRICTION['create']['success'],
            'restriction': new_restriction.as_dict(include_groups=True, include_users=True, include_resources=True)
        }
        status = HTTPStatus.CREATED.value
    finally:
        return content, status


@admin_required
def update(id: RestrictionId, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    new_values = newValues
    allowed_fields = {'name', 'startsAt', 'endsAt', 'isGlobal'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        restriction = Restriction.get(id)

        for field_name, new_value in new_values.items():
            field_name = snakecase(field_name)
            assert (field_name is not None) and hasattr(restriction, field_name), \
                'restriction has no {} field'.format(field_name)
            setattr(restriction, field_name, new_value)
        restriction.save()
        for user in restriction.get_all_affected_users():
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=True)
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except NoResultFound:
        content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['update']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['update']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def delete(id: RestrictionId) -> Tuple[Content, HttpStatusCode]:
    try:
        restriction_to_destroy = Restriction.get(id)
        users = restriction_to_destroy.get_all_affected_users()
        restriction_to_destroy.destroy()
        for user in users:
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, HTTPStatus.FORBIDDEN.value
    except NoResultFound:
        content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        content, status = {'msg': GENERAL['internal_error'] + str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['delete']['success']}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def apply_to_user(restriction_id: RestrictionId, user_id: UserId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        user = User.get(user_id)
        restriction.apply_to_user(user)
        ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=True)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': USER['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['users']['apply']['failure']['duplicate']}, HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['users']['apply']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['users']['apply']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def apply_to_group(restriction_id: RestrictionId, group_id: GroupId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        group = Group.get(group_id)
        restriction.apply_to_group(group)
        for user in group.users:
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=True)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['groups']['apply']['failure']['duplicate']}, HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['groups']['apply']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['groups']['apply']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def apply_to_resource(restriction_id: RestrictionId, resource_uuid: ResourceId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        resource = Resource.get(resource_uuid)
        restriction.apply_to_resource(resource)
        for user in restriction.get_all_affected_users():
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=True)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': RESOURCE['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['resources']['apply']['failure']['duplicate']}, HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['resources']['apply']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['resources']['apply']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def apply_to_resources_by_hostname(restriction_id: RestrictionId, hostname: str) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        resources = Resource.get_by_hostname(hostname)
        if resources:
            restriction.apply_to_resources(resources)
            for user in restriction.get_all_affected_users():
                ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=True)
        else:
            raise NoResultFound
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': NODES['hostname']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['hosts']['apply']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['hosts']['apply']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def add_schedule(restriction_id: RestrictionId, schedule_id: ScheduleId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        schedule = RestrictionSchedule.get(schedule_id)
        restriction.add_schedule(schedule)
        have_users_permissions_increased = len(restriction.schedules) > 1  # if added another schedule
        for user in restriction.get_all_affected_users():
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': SCHEDULE['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['schedules']['add']['failure']['duplicate']}, HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['schedules']['add']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['schedules']['add']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_from_user(restriction_id: RestrictionId, user_id: UserId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        user = User.get(user_id)
        restriction.remove_from_user(user)
        ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': USER['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['users']['remove']['failure']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['users']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['users']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_from_group(restriction_id: RestrictionId, group_id: GroupId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        group = Group.get(group_id)
        restriction.remove_from_group(group)
        for user in group.users:
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': GENERAL['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['groups']['remove']['failure']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['groups']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['groups']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_from_resource(restriction_id: RestrictionId, resource_uuid: ResourceId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        resource = Resource.get(resource_uuid)
        restriction.remove_from_resource(resource)
        for user in restriction.get_all_affected_users():
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': RESOURCE['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['resources']['remove']['failure']['not_found']}, \
            HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['resources']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['resources']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_from_resources_by_hostname(restriction_id: RestrictionId, hostname: str) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        resources = Resource.get_by_hostname(hostname)
        if resources:
            restriction.remove_from_resources(resources)
            for user in restriction.get_all_affected_users():
                ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
        else:
            raise NoResultFound
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': NODES['hostname']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['hosts']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['hosts']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_schedule(restriction_id: RestrictionId, schedule_id: ScheduleId) -> Tuple[Content, HttpStatusCode]:
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        schedule = RestrictionSchedule.get(schedule_id)
        restriction.remove_schedule(schedule)
        have_users_permissions_increased = len(restriction.schedules) == 0  # if removed last schedule
        for user in restriction.get_all_affected_users():
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': RESTRICTION['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': SCHEDULE['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': RESTRICTION['schedules']['remove']['failure']['not_found']}, \
            HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': RESTRICTION['schedules']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESTRICTION['schedules']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status
