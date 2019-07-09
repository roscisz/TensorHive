from flask_jwt_extended import jwt_required
from tensorhive.models.Reservation import Reservation
from sqlalchemy.orm.exc import NoResultFound
from typing import List, Optional, Any, Dict, Tuple
from tensorhive.config import API
import logging
log = logging.getLogger(__name__)
R = API.RESPONSES['reservation']
G = API.RESPONSES['general']

# FIXME This will make sense when all controllers are in one file (like task.py)
Content = Dict[str, Any]
HttpStatusCode = int
ReservationId = int


@jwt_required
def update(id: ReservationId, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    new_values = newValues
    allowed_fields = {'title', 'description', 'resourceId', 'start', 'end'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        reservation = Reservation.get(id)

        for field_name, new_value in new_values.items():
            # Mapping API field name to column used by Reservation model
            if field_name in ['start', 'end']:
                # start -> starts_at, end -> ends_at
                field_name += 's_at'
            if field_name == 'resourceId':
                field_name = 'protected_resource_id'
            assert hasattr(reservation, field_name), 'reservation has no {} column'.format(field_name)
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
