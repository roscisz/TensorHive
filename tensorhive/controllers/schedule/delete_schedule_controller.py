from http import HTTPStatus
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.authorization import admin_required
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from tensorhive.config import API
S = API.RESPONSES['schedule']
G = API.RESPONSES['general']


@admin_required
def delete(id):
    try:
        schedule_to_destroy = RestrictionSchedule.get(id)
        schedule_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, HTTPStatus.FORBIDDEN.value
    except NoResultFound:
        content, status = {'msg': S['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': S['delete']['success']}, HTTPStatus.OK.value
    finally:
        return content, status
