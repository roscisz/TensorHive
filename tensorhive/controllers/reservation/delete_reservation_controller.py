from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation


@jwt_required
def delete(id):
    # TODO Implement
    raise NotImplementedError