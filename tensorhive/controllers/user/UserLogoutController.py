from flask_jwt_extended import get_raw_jwt
from tensorhive.models.auth.RevokedTokenModel import RevokedTokenModel
from connexion import NoContent

class LogoutUserController():

    @staticmethod
    def delete_logout(token_type):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
        except:
            return {
                'msg': '{} token has not been revoked due to error'.format(token_type)
            }, 501

        if not revoked_token.save_to_db():
            return NoContent, 500

        return {
                   'msg': '{} token has been revoked.'.format(token_type)
               }, 201