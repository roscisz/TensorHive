from flask_jwt_extended import JWTManager,get_jwt_identity
from tensorhive.models.auth.RevokedTokenModel import RevokedTokenModel
from tensorhive.config import AUTH
from tensorhive.models.user.UserModel import UserModel
from tensorhive.models.role.RoleModel import RoleModel


def init_jwt(app):
    for key,value in AUTH.FLASK_JWT.items():
        app.config[key] = value
    global jwt
    jwt = JWTManager(app)

    @jwt.token_in_blacklist_loader
    def is_token_on_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return RevokedTokenModel.is_jti_blacklisted(jti)

    @jwt.user_claims_loader
    def add_claims_to_access_token(current_user_id):
        #current_user = UserModel.find_by_username(current_user_name)
        roles = []
        if current_user_id is not None:
            found_users_roles = RoleModel.find_by_user_id(current_user_id)
            if found_users_roles is not None:
                for role in found_users_roles:
                    roles.append(role.name)
        return {'roles': roles}