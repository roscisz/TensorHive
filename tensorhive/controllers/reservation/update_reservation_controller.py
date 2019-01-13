from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation
from tensorhive.config import API
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']

@jwt_required
def update(reservation):
    if reservation['id'] is not None:
        try:
            found_reservation = Reservation.get(reservation['id'])
            found_reservation.title = reservation['title'] if reservation['title'] is not None else found_reservation.title
            found_reservation.description = reservation['description'] if reservation['description'] is not None else found_reservation.description
            found_reservation.protected_resource_id = reservation['resourceId'] if  reservation['resourceId'] is not None else found_reservation.protected_resource_id
            found_reservation.user_id = reservation['userId'] if reservation['userId'] is not None else found_reservation.user_id
            found_reservation.starts_at = reservation['start'] if reservation['start'] is not None else found_reservation.starts_at
            found_reservation.ends_at = reservation['end'] if reservation['end'] is not None else found_reservation.ends_at

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
                'reservation': found_reservation.as_dict
            }
            status = 201
    else:
            content = {'msg': G['bad_request']}
            status = 400

    return content, status

