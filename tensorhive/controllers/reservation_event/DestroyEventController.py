from tensorhive.models.reservation_event.ReservationEventModel import ReservationEventModel
from connexion import NoContent
from flask_jwt_extended import get_jwt_identity

class DestroyEventController():

    @staticmethod
    def delete(id):
        user_id = get_jwt_identity()
        if (ReservationEventModel.find_by_id(id) == user_id):
            if not ReservationEventModel.delete_by_id(id):
                return NoContent, 404
            return NoContent, 204
        else:
            return NoContent, 401