from http import HTTPStatus
from tensorhive.authorization import admin_required
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.Restriction import Restriction
from tensorhive.models.User import User
from tensorhive.models.Group import Group
from tensorhive.models.Resource import Resource
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['restriction']
U = API.RESPONSES['user']
GROUP = API.RESPONSES['group']
RESOURCE = API.RESPONSES['resource']
S = API.RESPONSES['schedule']
G = API.RESPONSES['general']


@admin_required
def remove_from_user(restriction_id, user_id):
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        user = User.get(user_id)
        restriction.remove_from_user(user)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': R['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': U['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': R['users']['remove']['failure']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': R['users']['remove']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': R['users']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_from_group(restriction_id, group_id):
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        group = Group.get(group_id)
        restriction.remove_from_group(group)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': R['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': G['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': R['groups']['remove']['failure']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': R['groups']['remove']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': R['groups']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_from_resource(restriction_id, resource_uuid):
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        resource = Resource.get(resource_uuid)
        restriction.remove_from_resource(resource)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': R['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': RESOURCE['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': R['resources']['remove']['failure']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': R['resources']['remove']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': R['resources']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_schedule(restriction_id, schedule_id):
    restriction = None
    try:
        restriction = Restriction.get(restriction_id)
        schedule = RestrictionSchedule.get(schedule_id)
        restriction.remove_schedule(schedule)
    except NoResultFound:
        if restriction is None:
            content, status = {'msg': R['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': S['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': R['schedules']['remove']['failure']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': R['schedules']['remove']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': R['schedules']['remove']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, HTTPStatus.OK.value
    finally:
        return content, status
