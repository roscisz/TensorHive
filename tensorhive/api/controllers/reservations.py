import datetime

from flask_jwt_extended import jwt_required
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController
from tensorhive.controllers.reservation_event.ListReservationEventsController import ListReservationEventsController
from tensorhive.controllers.reservation_event.DestroyEventController import DestroyEventController

@jwt_required
def post(reservation_event):
    '''Create new'''
    return CreateReservationEventController.create(reservation_event)


@jwt_required
def search(resources_ids=None, start=None, end=None):
    args = [resources_ids, start, end]
    all_args_none = all(a is None for a in args)

    if all_args_none:
        return ListReservationEventsController.all()
    else:
        # Filter reservations
        return ListReservationEventsController.get(resources_ids, start, end)


@jwt_required
def delete(id):
    '''Remove if exists'''
    return DestroyEventController.delete(id)