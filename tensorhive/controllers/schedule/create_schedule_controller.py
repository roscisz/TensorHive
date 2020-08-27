from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from datetime import datetime
from tensorhive.utils.Weekday import Weekday
from tensorhive.authorization import admin_required
from tensorhive.config import API
S = API.RESPONSES['schedule']
G = API.RESPONSES['general']


@admin_required
def create(schedule):
    try:
        days = []
        for day in schedule['scheduleDays']:
            days.append(Weekday[day])

        new_schedule = RestrictionSchedule(
            schedule_days=days,
            hour_start=datetime.strptime(schedule['hourStart'], "%H:%M").time(),
            hour_end=datetime.strptime(schedule['hourEnd'], "%H:%M").time()
        )
        new_schedule.save()
    except KeyError:
        # Invalid day
        content = {'msg': G['bad_request']}
        status = 422
    except AssertionError as e:
        content = {'msg': S['create']['failure']['invalid'].format(reason=e)}
        status = 422
    except Exception as e:
        content = {'msg': G['internal_error'] + str(e)}
        status = 500
    else:
        content = {
            'msg': S['create']['success'],
            'schedule': new_schedule.as_dict
        }
        status = 201
    finally:
        return content, status
