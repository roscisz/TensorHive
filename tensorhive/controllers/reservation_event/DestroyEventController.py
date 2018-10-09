from tensorhive.models.Reservation import Reservation
from connexion import NoContent
from flask_jwt_extended import get_jwt_identity


class DestroyEventController():

    @staticmethod
    def delete(id):
        raise NotImplementedError
        # user_id = get_jwt_identity()
        # if Reservation.get(id).user_id == user_id:
        #     if not Reservation.delete_by_id(id):
        #         return NoContent, 500
        #     return NoContent, 204
        # else:
        #     return NoContent, 404
