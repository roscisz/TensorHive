from flask_jwt_extended import create_access_token, get_jwt_identity
from tensorhive.models.User import User
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
import logging
log = logging.getLogger(__name__)


class CreateRefreshedUserTokenController():

    @staticmethod
    def create():
        try:
            current_user = User.get(id=get_jwt_identity())
            new_access_token = create_access_token(identity=current_user.id, fresh=False)
        except NoResultFound:
            content, status = 'User does not exist in database', 404
        except MultipleResultsFound:
            content, status = 'Internal error', 500
        else:
            content = {
                'msg': 'Refreshed token',
                'access_token': new_access_token
            }
            status = 201
        finally:
            log.error(content)
            if isinstance(content, str):
                content = {'msg': content}, status
            return content, status
