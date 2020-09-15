from http import HTTPStatus
from tensorhive.authorization import admin_required
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.Group import Group
from tensorhive.models.User import User
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
GROUP = API.RESPONSES['group']
U = API.RESPONSES['user']
G = API.RESPONSES['general']


@admin_required
def add_user(group_id, user_id):
    group = None
    try:
        group = Group.get(group_id)
        user = User.get(user_id)
        group.add_user(user)
    except NoResultFound:
        if group is None:
            content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': U['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException:
        content, status = {'msg': GROUP['users']['add']['failure']['duplicate']}, HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': GROUP['users']['add']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['users']['add']['success'], 'group': group.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status
