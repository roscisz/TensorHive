import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from flask_jwt_extended import get_jwt_claims, get_jwt_identity, jwt_required
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
from tensorhive.core.utils.ReservationVerifier import ReservationVerifier
from tensorhive.models.Reservation import Reservation
from tensorhive.models.User import User
from tensorhive.utils.DateUtils import DateUtils

log = logging.getLogger(__name__)
RESERVATION = API.RESPONSES['reservation']
GENERAL = API.RESPONSES['general']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
ReservationId = int
ResourceId = str


def get_all() -> Tuple[List[Any], HttpStatusCode]:
    return [
        reservation.as_dict for reservation in Reservation.all()
    ], 200


def get_selected(resources_ids: Optional[List[ResourceId]] = None, start: Optional[str] = None,
                 end: Optional[str] = None) -> Tuple[Union[List[Any], Content], HttpStatusCode]:
    # TODO This may need a decent refactor - give more freedom
    # All args are required at once, otherwise return 400
    all_not_none = resources_ids and start and end
    if all_not_none:
        try:
            start_as_datetime = DateUtils.parse_string(start)
            ends_as_datetime = DateUtils.parse_string(end)
            matches = list(Reservation.filter_by_uuids_and_time_range(
                resources_ids, start_as_datetime, ends_as_datetime))
            matches = [match.as_dict for match in matches]
        except (ValueError, AssertionError) as reason:
            content = {'msg': '{}. {}'.format(GENERAL['bad_request'], reason)}
            status = 400
        except Exception:
            content = {'msg': GENERAL['internal_error']}
            status = 500
        else:
            content = matches  # type: ignore
            status = 200
    else:
        content = {'msg': GENERAL['bad_request']}
        status = 400
    return content, status


@jwt_required
def get(resources_ids: Optional[List[ResourceId]] = None, start: Optional[str] = None, end: Optional[str] = None) \
        -> Tuple[Union[List[Any], Content], HttpStatusCode]:
    args = [resources_ids, start, end]
    all_args_none = all(a is None for a in args)

    if all_args_none:
        return get_all()
    else:
        # Filter reservations
        return get_selected(resources_ids, start, end)


@jwt_required
def create(reservation: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        new_reservation = Reservation(
            title=reservation['title'],
            description=reservation['description'],
            protected_resource_id=reservation['resourceId'],
            user_id=reservation['userId'],
            starts_at=reservation['start'],
            ends_at=reservation['end']
        )

        assert __is_admin_or_reservation_owner(new_reservation), GENERAL['unprivileged']

        user = User.get(get_jwt_identity())
        if ReservationVerifier.is_reservation_allowed(user, new_reservation):
            new_reservation.save()
            content = {
                'msg': RESERVATION['create']['success'],
                'reservation': new_reservation.as_dict
            }
            status = 201
        else:
            content = {
                'msg': RESERVATION['create']['failure']['forbidden']
            }
            status = 403

    except AssertionError as e:
        content = {'msg': RESERVATION['create']['failure']['invalid'].format(reason=e)}
        status = 422
    except Exception:
        content = {'msg': GENERAL['internal_error']}
        status = 500
    finally:
        return content, status


def to_db_column() -> Dict[str, str]:
    return {
        'title': 'title',
        'description': 'description',
        'resourceId': 'protected_resource_id',
        'start': 'starts_at',
        'end': 'ends_at',
    }


@jwt_required
def update(id: ReservationId, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
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

        assert __is_admin_or_reservation_owner(reservation), GENERAL['unprivileged']

        user = User.get(get_jwt_identity())
        if ReservationVerifier.is_reservation_allowed(user, reservation):
            reservation.save()
            content, status = {'msg': RESERVATION['update']['success'], 'reservation': reservation.as_dict}, 201
        else:
            content, status = {'msg': RESERVATION['update']['failure']['forbidden']}, 403
    except NoResultFound:
        content, status = {'msg': RESERVATION['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': RESERVATION['update']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    finally:
        return content, status


@jwt_required
def delete(id: ReservationId) -> Tuple[Content, HttpStatusCode]:
    try:
        # Fetch the reservation
        reservation_to_destroy = Reservation.get(id)

        # Must be privileged
        assert __is_admin_or_reservation_owner(reservation_to_destroy), GENERAL['unprivileged']

        # Destroy
        reservation_to_destroy.destroy()
    except AssertionError as error_message:
        content, status = {'msg': str(error_message)}, 403
    except NoResultFound:
        # FIXME It is theoretically possible that User.get() could also raise this exception
        content, status = {'msg': RESERVATION['not_found']}, 404
    except Exception as e:
        content, status = {'msg': GENERAL['internal_error'] + str(e)}, 500
    else:
        content, status = {'msg': RESERVATION['delete']['success']}, 200
    finally:
        return content, status


def __is_admin_or_reservation_owner(reservation: Reservation) -> bool:
    return 'admin' in get_jwt_claims()['roles'] or reservation.user_id == get_jwt_identity()
