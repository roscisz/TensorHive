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
        content, status = {'msg': str(error_message)}, 403
    except NoResultFound:
        content, status = {'msg': S['not_found']}, 404
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, 500
    else:
        content, status = {'msg': S['delete']['success']}, 200
    finally:
        return content, status
