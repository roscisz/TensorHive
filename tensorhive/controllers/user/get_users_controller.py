from flask_jwt_extended import jwt_required
from tensorhive.models.User import User


@jwt_required
def get():
    return [
        user.as_dict for user in User.all()
    ], 200


@jwt_required
def get_by_id(id):
    return User.get(id).as_dict, 200
