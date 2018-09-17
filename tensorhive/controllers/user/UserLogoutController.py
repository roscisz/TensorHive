from flask_jwt_extended import get_raw_jwt
from tensorhive.models.auth.RevokedTokenModel import RevokedTokenModel

class LogoutUserController():

    @staticmethod
    def delete_logout(type):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti=jti)
            revoked_token.save_to_db()
            return {
                'message': ' {} token has been revoked.'.format(type)
            }, 201
        except:
            return {
                       'message': '{} token has not been revoked due to error'.format(type)
                   }, 501
