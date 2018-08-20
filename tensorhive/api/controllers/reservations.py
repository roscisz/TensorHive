import datetime

from connexion import NoContent
from tensorhive.controllers.reservation_event.CreateReservationEventController import CreateReservationEventController
from tensorhive.controllers.reservation_event.ListReservationEventsController import ListReservationEventsController
from tensorhive.controllers.reservation_event.DestroyEventController import DestroyEventController

def post(reservation_event):
    '''Create new'''
    return CreateReservationEventController.create(reservation_event)

def search(resources_ids, start, end):
    '''Get selected'''
    return ListReservationEventsController.get(resources_ids, start, end)

def delete(id):
    '''Remove if exists'''
    return DestroyEventController.delete(id)