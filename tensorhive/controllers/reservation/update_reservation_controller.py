from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']


def to_db_column():
    return {
        'title': 'title',
        'description': 'description',
        'resourceId': 'protected_resource_id',
        'start': 'starts_at',
        'end': 'ends_at',
    }


@jwt_required
def update(id, newValues):
    new_values = newValues
    allowed_fields = {'title', 'description', 'resourceId', 'start', 'end'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        reservation = Reservation.get(id)

        for field_name, new_value in new_values.items():
            field_name = to_db_column().get(field_name)
            assert (field_name is not None) and hasattr(reservation, field_name), \
                'reservation has no {} field'.format(field_name)
            setattr(reservation, field_name, new_value)
        reservation.save()
    except NoResultFound:
        content, status = {'msg': R['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': R['update']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': R['update']['success'], 'reservation': reservation.as_dict}, 201
    finally:
        return content, status
