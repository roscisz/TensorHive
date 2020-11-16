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
    auth_patch = auth_patcher.get_patch(superuser=True)
    auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
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
