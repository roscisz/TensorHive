from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import jwt_required, get_jwt_identity
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from tensorhive.config import API
from tensorhive.database import db, flask_app
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']


@jwt_required
def delete(id):
    try:
        # Check identity
        current_user_id = get_jwt_identity()
        assert current_user_id, G['no_identity']

        with flask_app.app_context():
            # Check if the identity exists
            User.get(current_user_id)

            # Try to destroy
            reservation_to_destroy = Reservation.get(id)
            db.session.add(reservation_to_destroy)
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
