from tensorhive.models.Reservation import Reservation
from tensorhive.models.Resource import Resource
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from importlib import reload
from sqlalchemy.orm.exc import NoResultFound
import auth_patcher

import datetime
from datetime import timedelta
from tensorhive.utils.DateUtils import DateUtils
import json
import pytest

ENDPOINT = BASE_URI + '/reservations'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=True)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


def test_after_updating_restriction_reservations_that_are_no_longer_valid_should_get_cancelled(tables, client,
                                                                                               new_user,
                                                                                               restriction):
    new_user.save()

    # Create a restriction, assign user and resource to it
    restriction.starts_at = '2101-01-01T10:00:00.000Z'
    restriction.ends_at = '2101-01-05T10:00:00.000Z'
    restriction.apply_to_user(new_user)

    resource = Resource(id='0123456789012345678901234567890123456789')
    resource.save()
    restriction.apply_to_resource(resource)

    # Create a reservation in allowed timeframe (should succeed)
    data = {
        'title': 'Test reservation',
        'description': 'Test reservation',
        'resourceId': '0123456789012345678901234567890123456789',
        'userId': new_user.id,
        'start': '2101-01-02T10:00:00.000Z',
        'end': '2101-01-03T12:00:00.000Z'
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    reservation = Reservation.get(resp_json['reservation']['id'])

    assert reservation.is_cancelled is False

    # Update the restriction to make the reservation invalid
    data = {
        'startsAt': '2101-01-04T09:00:00.000Z'
    }
    resp = client.put(BASE_URI + '/restrictions/' + str(reservation.id), headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.OK
    assert reservation.is_cancelled is True


def test_update_past_reservation(tables, client, past_reservation, permissive_restriction):
    permissive_restriction.save()
    past_reservation.save()

    new_reservation_title = past_reservation.title + '111'
    resp = client.put(ENDPOINT + '/' + str(past_reservation.id), headers=HEADERS,
                      data=json.dumps({'title': new_reservation_title}))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['reservation']['title'] == new_reservation_title
    assert Reservation.get(past_reservation.id).title == new_reservation_title


def test_create_reservation_starting_in_the_past(tables, client, new_user, permissive_restriction):
    new_user.save()

    # Create a resource and assign it to the restriction
    resource = Resource(id='0123456789012345678901234567890123456789')
    resource.save()

    past_time = datetime.datetime.now() - timedelta(minutes=2)
    end_time = past_time + timedelta(hours=1)

    data = {
        'title': 'Test reservation',
        'description': 'Test reservation',
        'resourceId': '0123456789012345678901234567890123456789',
        'userId': new_user.id,
        'start': DateUtils.stringify_datetime_to_api_format(past_time),
        'end': DateUtils.stringify_datetime_to_api_format(end_time)
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert Reservation.get(resp_json['reservation']['id']) is not None


def test_delete_active_reservation(tables, client, active_reservation, permissive_restriction):
    permissive_restriction.save()
    active_reservation.save()

    resp = client.delete(ENDPOINT + '/' + str(active_reservation.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    with pytest.raises(NoResultFound):
        Reservation.get(active_reservation.id)
