from tensorhive.models.User import User
from tensorhive.models.Role import Role
from connexion import NoContent
from flask_jwt_extended import get_raw_jwt
from tensorhive.models.auth.RevokedTokenModel import RevokedTokenModel

class DeleteUserController():

    @staticmethod
    def delete(id):
        user = User.find_by_id(id)
        found_admin_roles = Role.find_by_user_id(id)
        if found_admin_roles is not None:
            for role in found_admin_roles:
                if (role.name == 'admin'):
                    return NoContent, 403
        else:
            return NoContent, 500

        if user is not None:
            if not user.delete_from_db():
                return NoContent, 500
            else:
                jti = get_raw_jwt()['jti']
                try:
                    revoked_token = RevokedTokenModel(jti=jti)
                except:
                    return {
                               'msg': 'Token has not been revoked due to error'
                           }, 501

                if not revoked_token.save_to_db():
                    return NoContent, 500
        else:
            return NoContent, 404
        return NoContent, 204