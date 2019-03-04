from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation
from tensorhive.config import API
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']


@jwt_required
def update(reservation):
    if reservation.get('id') is not None:
        try:
            found_reservation = Reservation.get(reservation['id'])

            updateable_field_names = ['title', 'description', 'start', 'end']

            for field_name in updateable_field_names:
                if reservation.get(field_name) is not None:
                    setattr(found_reservation, field_name, reservation[field_name])

            found_reservation.save()

        except AssertionError as e:
            content = {'msg': R['update']['failure']['invalid'].format(reason=e)}
            status = 422
        except Exception:
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
