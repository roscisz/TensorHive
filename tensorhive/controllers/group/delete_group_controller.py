from http import HTTPStatus
from tensorhive.authorization import admin_required
from tensorhive.models.Group import Group
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
GROUP = API.RESPONSES['group']
G = API.RESPONSES['general']


@admin_required
def delete(id):
    try:
        group_to_destroy = Group.get(id)
        group_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, HTTPStatus.FORBIDDEN.value
    except NoResultFound:
        content, status = {'msg': GROUP['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': GROUP['delete']['success']}, HTTPStatus.OK.value
    finally:
        return content, status
