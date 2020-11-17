from tensorhive.models.Reservation import Reservation
from tensorhive.models.Resource import Resource
from tensorhive.models.Restriction import Restriction
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from importlib import reload
import auth_patcher
from datetime import timedelta
from tensorhive.utils.DateUtils import DateUtils

import datetime
import json

ENDPOINT = BASE_URI + '/reservations'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=False)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


def test_create_reservation_unprivileged(tables, client, new_user):
    new_user.save()

    # A user by default does not have any access policies assigned to him, so he shouldn't
    # be able to create a reservation
    data = {
        'title': 'Test reservation',
        'description': 'Test reservation',
        'resourceId': '0123456789012345678901234567890123456789',
        'userId': new_user.id,
        'start': '2021-01-01T10:00:00.000Z',
        'end': '2021-01-01T12:00:00.000Z'
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_create_reservation(tables, client, new_user, restriction):
    new_user.save()

    # Create a restriction and assign it to the user
    restriction.starts_at = '2101-01-01T10:00:00.000Z'
    restriction.ends_at = '2101-01-05T10:00:00.000Z'
    restriction.apply_to_user(new_user)

    # Create a resource and assign it to the restriction
    resource = Resource(id='0123456789012345678901234567890123456789')
    resource.save()
    restriction.apply_to_resource(resource)

    # Try to create reservation for a period that the user has access to, as specified by the restriction.
    # Should succeed.
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

    assert resp.status_code == HTTPStatus.CREATED
    assert Reservation.get(resp_json['reservation']['id']) is not None


def test_create_reservation_with_an_indefinite_restriction(tables, client, new_user, restriction):
    new_user.save()

    # Create an indefinite restriction and assign it to the user
    restriction.starts_at = '2101-01-01T10:00:00.000Z'
    restriction.ends_at = None
    restriction.apply_to_user(new_user)

    # Create a resource and assign it to the restriction
    resource = Resource(id='0123456789012345678901234567890123456789')
    resource.save()
    restriction.apply_to_resource(resource)

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

    assert resp.status_code == HTTPStatus.CREATED
    assert Reservation.get(resp_json['reservation']['id']) is not None


def test_create_reservation_with_permissions_just_for_a_part_of_it(tables, client, new_user, restriction):
    new_user.save()

    # Create a restriction and assign it to the user
    restriction.starts_at = '2101-01-01T10:00:00.000Z'
    restriction.ends_at = '2101-01-05T10:00:00.000Z'
    restriction.apply_to_user(new_user)

    # Create a resource and assign it to the restriction
    resource = Resource(id='0123456789012345678901234567890123456789')
    resource.save()
    restriction.apply_to_resource(resource)

    # Try to create reservation for a period just partly covered by the restriction.
    data = {
        'title': 'Test reservation',
        'description': 'Test reservation',
        'resourceId': '0123456789012345678901234567890123456789',
        'userId': new_user.id,
        'start': '2101-01-04T10:00:00.000Z',
        'end': '2101-01-06T12:00:00.000Z'
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_create_reservation_outside_of_schedule(tables, client, new_user, restriction):
    new_user.save()

    # Create a restriction and assign it to the user
    restriction.starts_at = '2101-01-01T10:00:00.000Z'
    restriction.ends_at = '2101-01-05T10:00:00.000Z'
    restriction.apply_to_user(new_user)

    # Create a schedule and assign it to the restriction
    schedule = RestrictionSchedule(
        schedule_days='1234567',
        hour_start=datetime.time(8, 0, 0),
        hour_end=datetime.time(10, 0, 0)
    )
    schedule.save()
    restriction.add_schedule(schedule)

    # Create a resource and assign it to the restriction
    resource = Resource(id='0123456789012345678901234567890123456789')
    resource.save()
    restriction.apply_to_resource(resource)

    # Try to create reservation for a period not covered by the restriction.
    data = {
        'title': 'Test reservation',
        'description': 'Test reservation',
        'resourceId': '0123456789012345678901234567890123456789',
        'userId': new_user.id,
        'start': '2101-01-07T09:00:00.000Z',
        'end': '2101-01-07T10:30:00.000Z'
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_create_reservation_that_is_covered_by_two_separate_restrictions(tables, client, new_user):
    r1_start = '2101-01-01T00:00:00.000Z'
    r1_end = '2101-01-02T00:00:00.000Z'
    r2_start = '2101-01-02T00:00:00.000Z'
    r2_end = '2101-01-02T23:59:00.000Z'

    r1 = Restriction(name='FirstRestriction', starts_at=r1_start, ends_at=r1_end, is_global=False)
    r2 = Restriction(name='SecondRestriction', starts_at=r2_start, ends_at=r2_end, is_global=False)

    new_user.save()
    r1.apply_to_user(new_user)
    r2.apply_to_user(new_user)

    resource = Resource(id='0123456789012345678901234567890123456789')
    resource.save()
    r1.apply_to_resource(resource)
    r2.apply_to_resource(resource)

    data = {
        'title': 'Test reservation',
        'description': 'Test reservation',
        'resourceId': '0123456789012345678901234567890123456789',
        'userId': new_user.id,
        'start': '2101-01-01T10:00:00.000Z',
        'end': '2101-01-02T12:00:00.000Z'
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert Reservation.get(resp_json['reservation']['id']) is not None


def test_update_reservation(tables, client, future_reservation, permissive_restriction):
    permissive_restriction.save()
    future_reservation.save()

    new_reservation_title = future_reservation.title + '111'
    resp = client.put(ENDPOINT + '/' + str(future_reservation.id), headers=HEADERS,
                      data=json.dumps({'title': new_reservation_title}))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['reservation']['title'] == new_reservation_title
    assert Reservation.get(future_reservation.id).title == new_reservation_title


def test_update_reservation_unprivileged(tables, client, new_reservation_2, permissive_restriction):
    permissive_restriction.save()
    new_reservation_2.save()

    new_reservation_title = new_reservation_2.title + '111'
    resp = client.put(ENDPOINT + '/' + str(new_reservation_2.id), headers=HEADERS,
                      data=json.dumps({'title': new_reservation_title}))

    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_update_future_reservation_start(tables, client, future_reservation, permissive_restriction):
    permissive_restriction.save()
    future_reservation.save()

    new_reservation_start = future_reservation.start + timedelta(hours=1)
    resp = client.put(ENDPOINT + '/' + str(future_reservation.id), headers=HEADERS,
                      data=json.dumps({'start': DateUtils.stringify_datetime_to_api_format(new_reservation_start)}))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['reservation']['start'] == DateUtils.stringify_datetime(new_reservation_start)
    assert Reservation.get(future_reservation.id).start == new_reservation_start


def test_update_active_reservation_start_forbidden(tables, client, active_reservation, permissive_restriction):
    permissive_restriction.save()
    active_reservation.save()

    new_reservation_start = active_reservation.start + timedelta(hours=1)
    resp = client.put(ENDPOINT + '/' + str(active_reservation.id), headers=HEADERS,
                      data=json.dumps({'start':  DateUtils.stringify_datetime_to_api_format(new_reservation_start)}))

    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_update_past_reservation_forbidden(tables, client, past_reservation, permissive_restriction):
    permissive_restriction.save()
    past_reservation.save()

    new_reservation_title = past_reservation.title + '111'
    resp = client.put(ENDPOINT + '/' + str(past_reservation.id), headers=HEADERS,
                      data=json.dumps({'title': new_reservation_title}))

    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_delete_active_reservation_forbidden(tables, client, active_reservation, permissive_restriction):
    permissive_restriction.save()
    active_reservation.save()

    new_reservation_title = active_reservation.title + '111'
    resp = client.delete(ENDPOINT + '/' + str(active_reservation.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.FORBIDDEN
