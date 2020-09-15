from http import HTTPStatus
from flask_jwt_extended import jwt_required
from tensorhive.models.Restriction import Restriction
from tensorhive.models.User import User
from tensorhive.models.Group import Group
from tensorhive.models.Resource import Resource
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging

log = logging.getLogger(__name__)
R = API.RESPONSES['restriction']
G = API.RESPONSES['general']


@jwt_required
def get_all():
    return [
        restriction.as_dict(include_groups=True, include_users=True,
                            include_resources=True) for restriction in Restriction.all()
    ], HTTPStatus.OK.value


@jwt_required
def get_selected(user_id, include_user_groups, group_id, resource_id, schedule_id):
    try:
        # If a specific group is selected then groups are not included in the restriction information in response
        # The same applies to users and resources
        include_groups = group_id is None
        include_users = user_id is None
        include_resources = schedule_id is None

        restrictions = []
        if user_id is not None:
            user = User.get(user_id)
            restrictions.extend(user.get_restrictions(include_global=True, include_group=include_user_groups))
        if group_id is not None:
            group = Group.get(group_id)
            restrictions.extend(group.get_restrictions(include_global=True))
        if resource_id is not None:
            resource = Resource.get(resource_id)
            restrictions.extend(resource.get_restrictions(include_global=True))
        if schedule_id is not None:
            schedule = RestrictionSchedule.get(schedule_id)
            restrictions.extend(schedule.restrictions)

        # Take unique restrictions
        result = set(restrictions)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': G['bad_request']}, HTTPStatus.BAD_REQUEST.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = [restriction.as_dict(include_groups=include_groups, include_users=include_users,
                                               include_resources=include_resources) for restriction in result],\
                          HTTPStatus.OK.value
    finally:
        return content, status


@jwt_required
def get(user_id=None, include_user_groups=None, group_id=None, resource_id=None, schedule_id=None):
    args = [user_id, include_user_groups, group_id, resource_id, schedule_id]
    all_args_none = all(a is None for a in args)

    if all_args_none:
        return get_all()
    else:
        # Filter restrictions
        return get_selected(user_id, include_user_groups, group_id, resource_id, schedule_id)
