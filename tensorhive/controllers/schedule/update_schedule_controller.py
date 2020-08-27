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


@admin_required
def update(id, newValues):
    new_values = newValues
    allowed_fields = {'scheduleDays', 'hourStart', 'hourEnd'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        schedule = RestrictionSchedule.get(id)

        for field_name, new_value in new_values.items():
            # Mapping API field name to column used by Schedule model
            if field_name == 'scheduleDays':
                field_name = 'schedule_days'
                days = []
                for day in new_value:
                    days.append(Weekday[day])
                new_value = days
            if field_name in ['hourStart', 'hourEnd']:
                # hourStart -> hour_start, hourEnd -> hour_end
                field_name = 'hour_' + (field_name[4:]).lower()
                new_value = datetime.strptime(new_value, "%H:%M").time()
            assert hasattr(schedule, field_name), 'schedule has no {} column'.format(field_name)
            setattr(schedule, field_name, new_value)
        schedule.save()
    except NoResultFound:
        content, status = {'msg': S['not_found']}, 404
    except KeyError:
        # Invalid day
        content, status = {'msg': G['bad_request']}, 422
    except AssertionError as e:
        content, status = {'msg': S['update']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': S['update']['success'], 'schedule': schedule.as_dict}, 201
    finally:
        return content, status
