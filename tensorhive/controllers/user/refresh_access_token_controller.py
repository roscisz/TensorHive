from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_refresh_token_required
from tensorhive.models.User import User
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['token']
G = API.RESPONSES['general']


@jwt_refresh_token_required
def generate():
    new_access_token = create_access_token(identity=get_jwt_identity(), fresh=False)
    content = {
        'msg': R['refresh']['success'],
        'access_token': new_access_token
    }
    return content, 200
