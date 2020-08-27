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
    try:
        group_not_found = True
        group = Group.get(group_id)
        group_not_found = False
        user = User.get(user_id)
        group.add_user(user)
    except NoResultFound:
        if group_not_found:
            content, status = {'msg': GROUP['not_found']}, 404
        else:
            content, status = {'msg': U['not_found']}, 404
    except InvalidRequestException:
        content, status = {'msg': GROUP['users']['add']['failure']['duplicate']}, 409
    except AssertionError as e:
        content, status = {'msg': GROUP['users']['add']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': GROUP['users']['add']['success'], 'group': group.as_dict}, 201
    finally:
        return content, status
