from flask_jwt_extended import JWTManager
from tensorhive.models.auth.RevokedTokenModel import RevokedTokenModel
from tensorhive.config import AUTH


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
        return {'roles': ['admin','user']}