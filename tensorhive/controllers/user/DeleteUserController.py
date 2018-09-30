from tensorhive.models.user.UserModel import UserModel
from tensorhive.models.role.RoleModel import RoleModel
from connexion import NoContent
from flask_jwt_extended import create_access_token, create_refresh_token

class DeleteUserController():
    # TODO Add more user parameters

    @staticmethod
    def delete(id):
        user = UserModel.find_by_id(id)
        if user is not None:
            user.delete_from_db()
        else:
            return NoContent, 404
        return NoContent, 204