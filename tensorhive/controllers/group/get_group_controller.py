from flask_jwt_extended import jwt_required
from tensorhive.models.Group import Group
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
GROUP = API.RESPONSES['group']
G = API.RESPONSES['general']


@jwt_required
def get():
    return [
        group.as_dict for group in Group.all()
    ], 200


@jwt_required
def get_by_id(id):
    try:
        group = Group.get(id)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': GROUP['not_found']}, 404
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': GROUP['get']['success'], 'group': group.as_dict}, 200
    finally:
        return content, status
