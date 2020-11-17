from tensorhive.database import db_session
from tensorhive.models.RestrictionSchedule import RestrictionSchedule
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from sqlalchemy.orm.exc import NoResultFound
import auth_patcher
from importlib import reload

import datetime
import json
import pytest

ENDPOINT = BASE_URI + '/schedules'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=False)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


# POST /schedules
def test_create_schedule_unprivileged(tables, client):
    data = {
        'hourStart': '8:00',
        'hourEnd': '16:00',
        'scheduleDays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.FORBIDDEN


# GET /schedules
def test_get_list_of_schedules(tables, client):
    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 0

    client.post(ENDPOINT, headers=HEADERS, data=json.dumps({'hourStart': '8:00', 'hourEnd': '16:00',
                                                            'scheduleDays': ['Monday']}))
    assert resp.status_code == HTTPStatus.OK

    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 1


# GET /schedules/{id}
def test_get_schedule_by_id(tables, client, active_schedule):
    resp = client.get(ENDPOINT + '/' + str(active_schedule.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json['schedule']['id'] == active_schedule.id


# GET /schedules/{id} - nonexistent id
def test_get_nonexistent_schedule_by_id(tables, client):
    nonexistent_id = '777'
    resp = client.get(ENDPOINT + '/' + nonexistent_id, headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# DELETE /schedules/{id}
def test_delete_schedule_unprivileged(tables, client, active_schedule):
    id = active_schedule.id
    resp = client.delete(ENDPOINT + '/' + str(id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.FORBIDDEN


# PUT /schedules/{id}
def test_update_schedule_unprivileged(tables, client, active_schedule):
    active_schedule.hour_start = datetime.time(8, 0, 0)
    active_schedule.hour_end = datetime.time(10, 0, 0)
    active_schedule.save()

    data = {
        'hourStart': '8:30',
        'hourEnd': '9:30'
    }
    resp = client.put(ENDPOINT + '/' + str(active_schedule.id), headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.FORBIDDEN
