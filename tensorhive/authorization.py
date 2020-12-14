from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from tensorhive.models.RevokedToken import RevokedToken
from tensorhive.config import AUTH
from functools import wraps
from tensorhive.models.User import User
from tensorhive.database import db_session
from tensorhive.config import API
G = API.RESPONSES['general']


def decode_token(token):
    return {}


def init_jwt(app):
    for key, value in AUTH.FLASK_JWT.items():
        app.config[key] = value
    global jwt
    jwt = JWTManager(app)

    @jwt.token_in_blacklist_loader
    def is_token_on_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return RevokedToken.is_jti_blacklisted(jti)

    @jwt.user_claims_loader
    def add_claims_to_access_token(current_user_id):
        try:
            current_user = User.get(current_user_id)
            roles = current_user.role_names
        except Exception:
            roles = []
        finally:
            return {'roles': roles}


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if 'admin' in claims['roles']:
            return fn(*args, **kwargs)
        return {'msg': G['unprivileged']}, 403
    return wrapper
