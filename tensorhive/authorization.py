from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims
from tensorhive.models.RevokedToken import RevokedToken
from tensorhive.config import AUTH
from functools import wraps
from tensorhive.models.Role import Role


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
        #current_user = User.find_by_username(current_user_name)
        roles = []
        if current_user_id is not None:
            found_users_roles = Role.find_by_user_id(current_user_id)
            if found_users_roles is not None:
                for role in found_users_roles:
                    roles.append(role.name)
        return {'roles': roles}

# Decorator admin role jwt access only
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        for role in claims['roles']:
            if role == 'admin':
                return fn(*args, **kwargs)
        return {'message': 'Admin required!'}, 401
    return wrapper