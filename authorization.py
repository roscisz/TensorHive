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
    def add_claims_to_access_token(user):
		current_user_name = get_jwt_identity()
		current_user_id = UserModel.find_by_username(current_user).id
		roles = []
		for role in RoleModel.find_by_user_id(current_user_id)
			roles.append(role.name)
        return {'roles': roles}