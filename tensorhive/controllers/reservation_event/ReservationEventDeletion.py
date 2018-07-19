from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel
from connexion import NoContent
from flask import jsonify


class ReservationEventDeletion():

    @staticmethod
    def delete(id):
        if not ReservationEventModel.delete_by_id(id):
            return NoContent, 404
        return NoContent, 204