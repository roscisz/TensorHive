from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_refresh_token_required
from tensorhive.models.User import User
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES
G = API.RESPONSES['general']


@jwt_refresh_token_required
def generate():
    try:
        # Check identity
        current_user_id = get_jwt_identity()
        assert current_user_id, G['no_identity']

        # Check if users exists
        User.get(id=current_user_id)

        # Generate new token
        new_access_token = create_access_token(identity=current_user_id, fresh=False)
    except (NoResultFound, AssertionError) as e:
        log.error(e)
        content = {'msg': G['unauthorized']}
        status = 401
    except Exception as e:
        log.critical(e)
        content = {'msg': G['internal_error']}
        status = 500
    else:
        content = {
            'msg': R['token']['refresh']['success'],
            'access_token': new_access_token
        }
        status = 200
    finally:
        return content, status
