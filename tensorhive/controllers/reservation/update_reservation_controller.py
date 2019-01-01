from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation
from tensorhive.config import API
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']

@jwt_required
def update(reservation_id,reservation):
    if reservation_id is not None:
        try:
			found_reservation = get(reservation_id)
            found_reservation.title = reservation['title']
            found_reservation.description = reservation['description']
            found_reservation.protected_resource_id = reservation['resourceId']
            found_reservation.user_id = reservation['userId']
            found_reservation.starts_at = reservation['start']
            found_reservation.ends_at = reservation['end']

            found_reservation.save()

        except AssertionError as e:
            content = {'msg': R['update']['failure']['invalid'].format(reason=e)}
            status = 422
        except Exception as e:
            content = {'msg': G['internal_error']}
            status = 500
        else:
            content = {
                'msg': R['update']['success'],
                'reservation': new_reservation.as_dict
            }
            status = 201
    else:
            content = {'msg': G['bad_request']}
            status = 400

    return content, status