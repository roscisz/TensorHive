from tensorhive.models.Reservation import Reservation
from flask_jwt_extended import jwt_required
# from tensorhive.database import flask_app
from tensorhive.config import API
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']


@jwt_required
def create(reservation):
    try:
        new_reservation = Reservation(
            title=reservation['title'],
            description=reservation['description'],
            protected_resource_id=reservation['resourceId'],
            user_id=reservation['userId'],
            starts_at=reservation['start'],
            ends_at=reservation['end']
        )
        new_reservation.save()
    except AssertionError as e:
        content = {'msg': R['create']['failure']['invalid'].format(reason=e)}
        status = 422
    except Exception:
        content = {'msg': G['internal_error']}
        status = 500
    else:
        content = {
            'msg': R['create']['success'],
            'reservation': new_reservation.as_dict
        }
        status = 201
    finally:
        return content, status
