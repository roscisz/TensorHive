from http import HTTPStatus
from datetime import datetime
from tensorhive.utils.Weekday import Weekday
from tensorhive.authorization import admin_required
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
S = API.RESPONSES['schedule']
G = API.RESPONSES['general']


def to_db_column():
    return {
        'scheduleDays': 'schedule_days',
        'hourStart': 'hour_start',
        'hourEnd': 'hour_end'
    }


@admin_required
def update(id, newValues):
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
            field_name = to_db_column().get(field_name)
            assert (field_name is not None) and hasattr(schedule, field_name), \
                'schedule has no {} field'.format(field_name)
            setattr(schedule, field_name, new_value)
        schedule.save()
    except NoResultFound:
        content, status = {'msg': S['not_found']}, HTTPStatus.NOT_FOUND.value
    except KeyError:
        # Invalid day
        content, status = {'msg': G['bad_request']}, HTTPStatus.UNPROCESSABLE_ENTITY.value
    except AssertionError as e:
        content, status = {'msg': S['update']['failure']['assertions'].format(reason=e)}, \
                          HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': S['update']['success'], 'schedule': schedule.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status
