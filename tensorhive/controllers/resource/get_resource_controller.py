from http import HTTPStatus
from flask_jwt_extended import jwt_required
from tensorhive.controllers.nodes.infrastructure_controller import get_infrastructure
from tensorhive.models.Resource import Resource
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['resource']
G = API.RESPONSES['general']


@jwt_required
def get():
    get_infrastructure()  # Save new GPUs in database
    return [
        resource.as_dict for resource in Resource.all()
    ], HTTPStatus.OK.value


@jwt_required
def get_by_id(uuid):
    get_infrastructure()  # Save new GPUs in database
    try:
        resource = Resource.get(uuid)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': R['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': R['get']['success'], 'resource': resource.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status
