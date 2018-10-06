from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from connexion import NoContent
from flask import jsonify


class CreateReservationEventController():

    @staticmethod
    def create(reservation):
        new_reservation = Reservation(
            title=reservation['title'],
            description=reservation['description'],
            resource_id=reservation['resourceId'],
            user_id=reservation['userId'],
            start=reservation['start'],
            end=reservation['end']
        )

        if not new_reservation.save_to_db():
            return NoContent, 400
        return new_reservation.as_dict, 201
