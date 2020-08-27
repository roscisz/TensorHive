from flask_jwt_extended import jwt_required
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
S = API.RESPONSES['schedule']
G = API.RESPONSES['general']


@jwt_required
def get():
    return [
        schedule.as_dict for schedule in RestrictionSchedule.all()
    ], 200


@jwt_required
def get_by_id(id):
    try:
        schedule = RestrictionSchedule.get(id)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': S['not_found']}, 404
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': S['get']['success'], 'schedule': schedule.as_dict}, 200
    finally:
        return content, status
