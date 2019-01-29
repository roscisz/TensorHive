from flask_jwt_extended import get_raw_jwt
from tensorhive.models.RevokedToken import RevokedToken
from flask_jwt_extended import jwt_required, jwt_refresh_token_required
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['user']
G = API.RESPONSES['general']
T = API.RESPONSES['token']['revoke']


def logout(token_type):
    jti = get_raw_jwt()['jti']
    try:
        RevokedToken(jti=jti).save()
    except Exception:
        log.critical(G['internal_error'])
        log.critical(T['failure'].format(token_type=token_type))
        content = {'msg': G['internal_error']}
        status = 500
    else:
        content = {'msg': R['logout']['success']}
        status = 200
    finally:
        return content, status


@jwt_required
def logout_with_access_token():
    return logout('Access')


@jwt_refresh_token_required
def logout_with_refresh_token():
    return logout('Refresh')
