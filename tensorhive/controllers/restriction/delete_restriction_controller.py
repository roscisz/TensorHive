from http import HTTPStatus
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.authorization import admin_required
from tensorhive.models.Restriction import Restriction
from tensorhive.config import API
R = API.RESPONSES['restriction']
G = API.RESPONSES['general']


@admin_required
def delete(id):
    try:
        restriction_to_destroy = Restriction.get(id)
        restriction_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, HTTPStatus.FORBIDDEN.value
    except NoResultFound:
        content, status = {'msg': R['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': R['delete']['success']}, HTTPStatus.OK.value
    finally:
        return content, status
