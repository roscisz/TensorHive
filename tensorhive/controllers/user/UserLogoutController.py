from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import get_raw_jwt
from tensorhive.models.RevokedToken import RevokedToken
from tensorhive.config import API
R = API.RESPONSES['token']
G = API.RESPONSES['general']


class LogoutUserController():
    # TODO Use response mapping, e.g. token.revoke.error: some message
    @staticmethod
    def delete_logout(token_type):
        jti = get_raw_jwt()['jti']
        try:
            RevokedToken(jti=jti).save()
        except Exception as e:
            content = {'msg': G['internal_error']}
            status = 500
        else:
            content = {'msg': R['revoke']['success'].format(token_type=token_type)}
            status = 201
        finally:
            return content, status
