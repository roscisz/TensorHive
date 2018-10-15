from flask_jwt_extended import get_raw_jwt
from tensorhive.models.RevokedToken import RevokedToken
from flask_jwt_extended import jwt_required, jwt_refresh_token_required
from tensorhive.config import API
R = API.RESPONSES['token']
G = API.RESPONSES['general']


def logout(token_type):
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


@jwt_required
def logout_with_access_token():
    return logout('Access')


@jwt_refresh_token_required
def logout_with_refresh_token():
    return logout('Refresh')
