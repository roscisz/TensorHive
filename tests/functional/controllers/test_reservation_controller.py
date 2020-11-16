from tensorhive.models.Reservation import Reservation
from tensorhive.models.Resource import Resource
from tensorhive.models.Restriction import Restriction
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from importlib import reload
import auth_patcher
import tensorhive.controllers.reservation as sut

import datetime
import json

ENDPOINT = BASE_URI + '/reservations'


def setup_module(_):
    auth_patch = auth_patcher.get_patch(superuser=False)
    auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    auth_patch.stop()


def test_create_reservation_without_permissions(tables, client, new_user):
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


def test_create_reservation_with_proper_permissions(tables, client, new_user, restriction):
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
