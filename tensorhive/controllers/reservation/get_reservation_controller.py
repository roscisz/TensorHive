from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation
from typing import List
from tensorhive.config import API
G = API.RESPONSES['general']


@jwt_required
def get_all():
    return [
        reservation.as_dict for reservation in Reservation.all()
    ], 200


@jwt_required
def get_selected(resources_ids: List, start: str, end: str):
    # TODO This may need a decent refactor - give more freedom
    # All args are required at once, otherwise return 400
    all_not_none = resources_ids and start and end
    if all_not_none:
        try:
            start_as_datetime = Reservation.parsed_input_datetime(start)
            ends_as_datetime = Reservation.parsed_input_datetime(end)
            matches = list(Reservation.filter_by_uuids_and_time_range(
                resources_ids, start_as_datetime, ends_as_datetime))
            matches = [match.as_dict for match in matches]
        except (ValueError, AssertionError) as reason:
            content = {'msg': '{}. {}'.format(G['bad_request'], reason)}
            status = 400
        except Exception:
            content = {'msg': G['internal_error']}
            status = 500
        else:
            content = matches  # type: ignore
            status = 200
    else:
        content = {'msg': G['bad_request']}
        status = 400
    return content, status


@jwt_required
def get(resources_ids=None, start=None, end=None):
    args = [resources_ids, start, end]
    all_args_none = all(a is None for a in args)

    if all_args_none:
        return get_all()
    else:
        # Filter reservations
        return get_selected(resources_ids, start, end)
