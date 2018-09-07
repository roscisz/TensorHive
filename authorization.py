from flask_jwt_extended import JWTManager
from tensorhive.models.auth import RevokedTokenModel
jwt = JWTManager()

def init_jwt(app, API_CONFIG):
    for key,value in API_CONFIG.JWT.items():
        app.config["test"] = value

    jwt = JWTManager(app)

@jwt.token_in_blacklist_loader
def is_token_on_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedTokenModel.is_jti_blacklisted(jti)