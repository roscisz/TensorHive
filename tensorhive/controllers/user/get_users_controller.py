from flask_jwt_extended import jwt_required
from tensorhive.models.User import User
from sqlalchemy.orm.exc import NoResultFound
from connexion import NoContent
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
G = API.RESPONSES['general']
U = API.RESPONSES['user']


@jwt_required
def get():
    return [
        user.as_dict for user in User.all()
    ], 200


@jwt_required
def get_by_id(id):
    # Dead code, web app is currently not using it
    try:
        user = User.get(id)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': U['not_found']}, 404
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': U['get']['success'], 'user': user.as_dict}, 200
    finally:
        return content, status
