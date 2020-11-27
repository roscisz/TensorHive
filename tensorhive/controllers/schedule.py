import logging
from datetime import datetime
from http import HTTPStatus
from typing import Any, Dict, List, Tuple
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.authorization import admin_required
from tensorhive.config import API
from tensorhive.core.utils.ReservationVerifier import ReservationVerifier
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from tensorhive.utils.Weekday import Weekday
from stringcase import snakecase

log = logging.getLogger(__name__)
SCHEDULE = API.RESPONSES['schedule']
GENERAL = API.RESPONSES['general']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
ScheduleId = int


@jwt_required
def get() -> Tuple[List[Any], HttpStatusCode]:
    return [
        schedule.as_dict() for schedule in RestrictionSchedule.all()
    ], HTTPStatus.OK.value


@jwt_required
def get_by_id(id: ScheduleId) -> Tuple[Content, HttpStatusCode]:
    try:
        schedule = RestrictionSchedule.get(id)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': SCHEDULE['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': SCHEDULE['get']['success'], 'schedule': schedule.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def create(schedule: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        days = [Weekday[day] for day in schedule['scheduleDays']]
        new_schedule = RestrictionSchedule(
            schedule_days=days,
            hour_start=datetime.strptime(schedule['hourStart'], "%H:%M").time(),
            hour_end=datetime.strptime(schedule['hourEnd'], "%H:%M").time()
        )
        new_schedule.save()
    except KeyError:
        # Invalid day
        content = {'msg': GENERAL['bad_request']}
        status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except AssertionError as e:
        content = {'msg': SCHEDULE['create']['failure']['invalid'].format(reason=e)}
        status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        content = {'msg': GENERAL['internal_error'] + str(e)}
        status = HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content = {
            'msg': SCHEDULE['create']['success'],
            'schedule': new_schedule.as_dict()
        }
        status = HTTPStatus.CREATED.value
    finally:
        return content, status


@admin_required
def update(id, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    new_values = newValues
    allowed_fields = {'scheduleDays', 'hourStart', 'hourEnd'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        schedule = RestrictionSchedule.get(id)

        for field_name, new_value in new_values.items():
            if field_name == 'scheduleDays':
                new_value = [Weekday[day] for day in new_value]
            if field_name in ['hourStart', 'hourEnd']:
                new_value = datetime.strptime(new_value, "%H:%M").time()
            field_name = snakecase(field_name)
            assert (field_name is not None) and hasattr(schedule, field_name), \
                'schedule has no {} field'.format(field_name)
            setattr(schedule, field_name, new_value)
        schedule.save()
        for restriction in schedule.restrictions:
            for user in restriction.get_all_affected_users():
                ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=True)
                ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased=False)
    except NoResultFound:
        content, status = {'msg': SCHEDULE['not_found']}, HTTPStatus.NOT_FOUND.value
    except KeyError:
        # Invalid day
        content, status = {'msg': GENERAL['bad_request']}, HTTPStatus.UNPROCESSABLE_ENTITY.value
    except AssertionError as e:
        content, status = {'msg': SCHEDULE['update']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': SCHEDULE['update']['success'], 'schedule': schedule.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


@admin_required
def delete(id: ScheduleId) -> Tuple[Content, HttpStatusCode]:
    try:
        schedule_to_destroy = RestrictionSchedule.get(id)
        restrictions = schedule_to_destroy.restrictions
        schedule_to_destroy.destroy()
        for restriction in restrictions:
            have_users_permissions_increased = len(restriction.schedules) == 0  # if deleted last schedule
            for user in restriction.get_all_affected_users():
                ReservationVerifier.update_user_reservations_statuses(user, have_users_permissions_increased)
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, HTTPStatus.FORBIDDEN.value
    except NoResultFound:
        content, status = {'msg': SCHEDULE['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        content, status = {'msg': GENERAL['internal_error'] + str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': SCHEDULE['delete']['success']}, HTTPStatus.OK.value
    finally:
        return content, status
