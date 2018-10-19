from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from tensorhive.config import API
from tensorhive.database import db_session
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']


@jwt_required
def delete(id):
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt_claims()

        # Fetch the reservation
        reservation_to_destroy = Reservation.get(id)

        # Must be priviliged
        is_admin = 'admin' in claims['roles']
        is_owner = reservation_to_destroy.user_id == current_user_id
        assert is_owner or is_admin, G['unpriviliged']

        # Destroy
        reservation_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, 403
    except NoResultFound:
        # FIXME It is theoretically posibble that User.get() could also raise this exception
        content, status = {'msg': R['not_found']}, 404
    except Exception as e:
        content, status = {'msg': G['internal_error'] + str(e)}, 500
    else:
        content, status = {'msg': R['delete']['success']}, 200
    finally:
        return content, status
