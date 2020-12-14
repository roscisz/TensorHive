import logging
from http import HTTPStatus
from typing import Any, Dict, List, Tuple
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
from tensorhive.controllers.nodes import get_infrastructure
from tensorhive.models.Resource import Resource

log = logging.getLogger(__name__)
RESOURCE = API.RESPONSES['resource']
GENERAL = API.RESPONSES['general']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
ResourceUUID = int


@jwt_required
def get() -> Tuple[List[Any], HttpStatusCode]:
    get_infrastructure()  # Save new GPUs in database
    return [
        resource.as_dict() for resource in Resource.all()
    ], HTTPStatus.OK.value


@jwt_required
def get_by_id(uuid: ResourceUUID) -> Tuple[Content, HttpStatusCode]:
    get_infrastructure()  # Save new GPUs in database
    try:
        resource = Resource.get(uuid)
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': RESOURCE['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': RESOURCE['get']['success'], 'resource': resource.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status
