import datetime

from connexion import NoContent
from tensorhive.controllers.reservation_event.ReservationEventCreation import ReservationEventCreation
from tensorhive.controllers.reservation_event.AllReservationEvents import AllReservationEvents
from tensorhive.controllers.reservation_event.ReservationEventDeletion import ReservationEventDeletion

def post(reservation_event):
    '''Create new'''
    return ReservationEventCreation.create(reservation_event)

def search():
    '''Get all'''
    return AllReservationEvents.get()

def delete(id):
    '''Remove if exists'''
    return ReservationEventDeletion.delete(id)