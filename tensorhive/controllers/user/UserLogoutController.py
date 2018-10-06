from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_raw_jwt
from tensorhive.models.RevokedToken import RevokedToken


class LogoutUserController():
    # TODO Use response mapping, e.g. token.revoke.error: some message
    @staticmethod
    def delete_logout(token_type):
        jti = get_raw_jwt()['jti']
        try:
            RevokedToken.create(jti=jti)
        except SQLAlchemyError:
            content = '{} token has not been revoked due to an error'.format(token_type)
            status = 500
        else:
            content, status = '{} token has been revoked.'.format(token_type), 201
        finally:
            return {'msg': content}, status
