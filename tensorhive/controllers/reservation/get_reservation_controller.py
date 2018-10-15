from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation


@jwt_required
def all():
    return [
        reservation.as_dict for reservation in Reservation.all()
    ], 200


@jwt_required
def selected(resources_ids, start, end):
    # All args are required at once, otherwise return 400
    all_not_none = resources_ids and start and end
    if all_not_none:
        reservations = list(Reservation.filter_by_uuids_and_time_range(
            resources_ids, start, end))
        content = [reservation.as_dict for reservation in reservations]
        return content, 200
    else:
        return 'Bad request', 400


@jwt_required
def get(resources_ids=None, start=None, end=None):
    args = [resources_ids, start, end]
    all_args_none = all(a is None for a in args)

    if all_args_none:
        return all()
    else:
        # Filter reservations
        return selected(resources_ids, start, end)
