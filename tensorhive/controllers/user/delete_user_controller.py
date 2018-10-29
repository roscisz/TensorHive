from sqlalchemy.orm.exc import NoResultFound
from tensorhive.models.User import User
from tensorhive.database import db_session
from flask_jwt_extended import get_jwt_identity
from tensorhive.authorization import admin_required
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['user']
G = API.RESPONSES['general']


@admin_required
def delete(id):
    try:
        current_user_id = get_jwt_identity()

        # User is not allowed to delete his own account
        assert id != current_user_id, R['delete']['self']

        # Fetch the user and destroy
        user_to_destroy = User.get(id)
        user_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, 403
    except NoResultFound:
        content, status = {'msg': R['not_found']}, 404
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, 500
    else:
        content, status = {'msg': R['delete']['success']}, 200
    finally:
        return content, status
