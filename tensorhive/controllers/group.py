import logging
from http import HTTPStatus
from typing import Any, Dict, List, Tuple
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.authorization import admin_required
from tensorhive.config import API
from tensorhive.core.utils.ReservationVerifier import ReservationVerifier
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from tensorhive.models.Group import Group
from tensorhive.models.User import User
from stringcase import snakecase

log = logging.getLogger(__name__)
GROUP = API.RESPONSES['group']
USER = API.RESPONSES['user']
GENERAL = API.RESPONSES['general']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
GroupId = int
UserId = int


@jwt_required
def get(only_default: bool = False) -> Tuple[List[Any], HttpStatusCode]:
    if only_default:
        groups = Group.get_default_groups()
    else:
        groups = Group.all()
    return [
        group.as_dict() for group in groups
    ], HTTPStatus.OK.value


@jwt_required
def get_by_id(id: GroupId) -> Tuple[Content, HttpStatusCode]:
    try:
        group = Group.get(id)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['get']['success'], 'group': group.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def create(group: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        new_group = Group(
            name=group['name'],
            is_default=group['isDefault'] if 'isDefault' in group else False
        )
        new_group.save()
    except AssertionError as e:
        content = {'msg': GROUP['create']['failure']['invalid'].format(reason=e)}
        status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        content = {'msg': GENERAL['internal_error'] + str(e)}
        status = HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content = {
            'msg': GROUP['create']['success'],
            'group': new_group.as_dict()
        }
        status = HTTPStatus.CREATED.value
    finally:
        return content, status


@admin_required
def update(id: GroupId, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    new_values = newValues
    allowed_fields = {'name', 'isDefault'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        group = Group.get(id)

        for field_name, new_value in new_values.items():
            field_name = snakecase(field_name)
            assert hasattr(group, field_name), 'group has no {} field'.format(field_name)
            setattr(group, field_name, new_value)
        group.save()
    except NoResultFound:
        content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': GROUP['update']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['update']['success'], 'group': group.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def delete(id: GroupId) -> Tuple[Content, HttpStatusCode]:
    try:
        group_to_destroy = Group.get(id)
        users = group_to_destroy.users
        group_to_destroy.destroy()
        for user in users:
            ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, HTTPStatus.FORBIDDEN.value
    except NoResultFound:
        content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        content, status = {'msg': GENERAL['internal_error'] + str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['delete']['success']}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def add_user(group_id: GroupId, user_id: UserId) -> Tuple[Content, HttpStatusCode]:
    group = None
    try:
        group = Group.get(group_id)
        user = User.get(user_id)
        group.add_user(user)
        ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=True)
    except NoResultFound:
        if group is None:
            content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': USER['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': GROUP['users']['add']['failure']['duplicate']}, HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': GROUP['users']['add']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['users']['add']['success'], 'group': group.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def remove_user(group_id: GroupId, user_id: UserId) -> Tuple[Content, HttpStatusCode]:
    group = None
    try:
        group = Group.get(group_id)
        user = User.get(user_id)
        group.remove_user(user)
        ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except NoResultFound:
        if group is None:
            content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': USER['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': GROUP['users']['remove']['failure']['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': GROUP['users']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['users']['remove']['success'], 'group': group.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status
