from datetime import time, timedelta
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.Resource import Resource


def check_schedules(start_date, end_date, schedules):
    reservation_allowed = False
    while True:
        start_date_changed = False
        for schedule in schedules:
            day = start_date.weekday() + 1
            if str(day) in schedule.schedule_days and schedule.hour_start <= start_date.time():
                if schedule.hour_end == time(hour=23, minute=59):
                    start_date = start_date.replace(hour=0, minute=0) + timedelta(days=1)
                elif start_date.time() < schedule.hour_end:
                    start_date = start_date.replace(hour=schedule.hour_end.hour, minute=schedule.hour_end.minute)
                else:
                    continue
                start_date_changed = True
                if start_date >= end_date:
                    reservation_allowed = True
                    break
        if reservation_allowed or not start_date_changed:
            break
    return start_date


def is_reservation_allowed(user, reservation):
    try:
        resource = Resource.get(reservation.protected_resource_id)
    except NoResultFound:
        return False

    user_restrictions = user.get_restrictions(include_group=True)
    # get global restrictions or applied to selected resource
    restrictions = []
    for restriction in user_restrictions:
        if restriction.is_global or resource in restriction.resources:
            restrictions.append(restriction)

    # time interval required to create restriction
    start_date = reservation.starts_at
    end_date = reservation.ends_at

    reservation_allowed = False
    while True:
        start_date_changed = False
        for restriction in restrictions:
            if restriction.starts_at <= start_date < restriction.ends_at:
                schedules = restriction.schedules
                if not schedules:
                    start_date = restriction.ends_at
                    start_date_changed = True
                else:
                    date = check_schedules(start_date, end_date, schedules)
                    if date > start_date:
                        start_date_changed = True
                        start_date = date
                if start_date >= end_date:
                    reservation_allowed = True
                    break
        if reservation_allowed or not start_date_changed:
            break
    return reservation_allowed


def check_user_reservations(user, increase_permissions):
    reservations = user.get_reservations(include_cancelled=True)
    for reservation in reservations:
        if increase_permissions:
            if reservation.is_cancelled and is_reservation_allowed(user, reservation) \
                    and not reservation.would_interfere():
                reservation.is_cancelled = False
                reservation.save()
        else:
            if not reservation.is_cancelled and not is_reservation_allowed(user, reservation):
                reservation.is_cancelled = True
                reservation.save()
