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
def apply_to_user(restriction_id, user_id):
    try:
        restriction_not_found = True
        restriction = Restriction.get(restriction_id)
        restriction_not_found = False
        user = User.get(user_id)
        restriction.apply_to_user(user)
    except NoResultFound:
        if restriction_not_found:
            content, status = {'msg': R['not_found']}, 404
        else:
            content, status = {'msg': U['not_found']}, 404
    except InvalidRequestException as e:
        content, status = {'msg': R['users']['apply']['failure']['duplicate']}, 409
    except AssertionError as e:
        content, status = {'msg': R['users']['apply']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': R['users']['apply']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, 201
    finally:
        return content, status


@admin_required
def apply_to_group(restriction_id, group_id):
    try:
        restriction_not_found = True
        restriction = Restriction.get(restriction_id)
        restriction_not_found = False
        group = Group.get(group_id)
        restriction.apply_to_group(group)
    except NoResultFound:
        if restriction_not_found:
            content, status = {'msg': R['not_found']}, 404
        else:
            content, status = {'msg': GROUP['not_found']}, 404
    except InvalidRequestException as e:
        content, status = {'msg': R['groups']['apply']['failure']['duplicate']}, 409
    except AssertionError as e:
        content, status = {'msg': R['groups']['apply']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': R['groups']['apply']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, 201
    finally:
        return content, status


@admin_required
def apply_to_resource(restriction_id, resource_uuid):
    try:
        restriction_not_found = True
        restriction = Restriction.get(restriction_id)
        restriction_not_found = False
        resource = Resource.get(resource_uuid)
        restriction.apply_to_resource(resource)
    except NoResultFound:
        if restriction_not_found:
            content, status = {'msg': R['not_found']}, 404
        else:
            content, status = {'msg': RESOURCE['not_found']}, 404
    except InvalidRequestException as e:
        content, status = {'msg': R['resources']['apply']['failure']['duplicate']}, 409
    except AssertionError as e:
        content, status = {'msg': R['resources']['apply']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': R['resources']['apply']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, 201
    finally:
        return content, status


@admin_required
def add_schedule(restriction_id, schedule_id):
    try:
        restriction_not_found = True
        restriction = Restriction.get(restriction_id)
        restriction_not_found = False
        schedule = RestrictionSchedule.get(schedule_id)
        restriction.add_schedule(schedule)
    except NoResultFound:
        if restriction_not_found:
            content, status = {'msg': R['not_found']}, 404
        else:
            content, status = {'msg': S['not_found']}, 404
    except InvalidRequestException as e:
        content, status = {'msg': R['schedules']['add']['failure']['duplicate']}, 409
    except AssertionError as e:
        content, status = {'msg': R['schedules']['add']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': R['schedules']['add']['success'],
                           'restriction': restriction.as_dict(include_groups=True, include_users=True,
                                                              include_resources=True)}, 201
    finally:
        return content, status
