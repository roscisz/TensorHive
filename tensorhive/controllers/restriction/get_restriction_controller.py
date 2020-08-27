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
    ], 200


@jwt_required
def get_selected(user_id, include_user_groups, group_id, resource_id, schedule_id):
    try:
        include_groups = True
        include_users = True
        include_resources = True
        restrictions = []
        if user_id is not None:
            user = User.get(user_id)
            restrictions.append(set(user.get_restrictions(include_global=True, include_group=include_user_groups)))
            include_users = False
        if group_id is not None:
            group = Group.get(group_id)
            restrictions.append(set(group.get_restrictions(include_global=True)))
            include_groups = False
        if resource_id is not None:
            resource = Resource.get(resource_id)
            restrictions.append(set(resource.get_restrictions(include_global=True)))
            include_resources = False
        if schedule_id is not None:
            schedule = RestrictionSchedule.get(schedule_id)
            restrictions.append(set(schedule.restrictions))

        result = restrictions[0]
        for restriction in restrictions:
            result = result & restriction
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': G['bad_request']}, 400
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = [restriction.as_dict(include_groups=include_groups, include_users=include_users,
                                               include_resources=include_resources) for restriction in result], 200
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
