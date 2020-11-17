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
    auth_patches = auth_patcher.get_patches(superuser=True)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


# POST /schedules
def test_create_schedule(tables, client):
    data = {
        'hourStart': '8:00',
        'hourEnd': '16:00',
        'scheduleDays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert RestrictionSchedule.get(resp_json['schedule']['id']) is not None


# POST /schedules - missing data
def test_create_schedule_with_missing_start_hour(tables, client):
    data = {
        'hourEnd': '16:00',
        'scheduleDays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.BAD_REQUEST


# POST /schedules - incorrect data
def test_create_schedule_with_nonexistent_schedule_days(tables, client):
    data = {
        'hourStart': '8:00',
        'hourEnd': '16:00',
        'scheduleDays': ['Monday', 'Tuesday', 'SpecialDay']
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# POST /schedules - missing data
def test_create_schedule_with_no_schedule_days(tables, client):
    data = {
        'hourStart': '8:00',
        'hourEnd': '16:00'
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.BAD_REQUEST


# DELETE /schedules/{id}
def test_delete_schedule(tables, client, active_schedule):
    id = active_schedule.id
    resp = client.delete(ENDPOINT + '/' + str(id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    with pytest.raises(NoResultFound):
        RestrictionSchedule.get(id)


# DELETE /schedules/{id} - nonexistent id
def test_delete_nonexistent_schedule(tables, client):
    nonexistent_id = '777'
    resp = client.delete(ENDPOINT + '/' + nonexistent_id, headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /schedules/{id}
def test_update_schedule(tables, client, active_schedule):
    active_schedule.hour_start = datetime.time(8, 0, 0)
    active_schedule.hour_end = datetime.time(10, 0, 0)
    active_schedule.save()

    data = {
        'hourStart': '8:30',
        'hourEnd': '9:30'
    }
    resp = client.put(ENDPOINT + '/' + str(active_schedule.id), headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.OK
    assert active_schedule.hour_start == datetime.time(8, 30, 0)
    assert active_schedule.hour_end == datetime.time(9, 30, 0)


# PUT /schedules/{id} - nonexistent id
def test_update_nonexistent_schedule(tables, client):
    nonexistent_id = '777'
    data = {
        'hourStart': '8:30',
        'hourEnd': '9:30'
    }
    resp = client.put(ENDPOINT + '/' + nonexistent_id, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /schedules/{id} - incorrect data
def test_update_schedule_with_invalid_start_and_end_hours(tables, client, active_schedule):
    active_schedule.hour_start = datetime.time(8, 0, 0)
    active_schedule.hour_end = datetime.time(10, 0, 0)
    active_schedule.save()

    data = {
        'hourStart': '15:30',
        'hourEnd': '9:30'
    }
    resp = client.put(ENDPOINT + '/' + str(active_schedule.id), headers=HEADERS, data=json.dumps(data))

    db_session.remove()  # make sure we'll get the restriction from the DB, and not from memory
    active_schedule = RestrictionSchedule.get(active_schedule.id)
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert active_schedule.hour_start == datetime.time(8, 0, 0)
    assert active_schedule.hour_end == datetime.time(10, 0, 0)
