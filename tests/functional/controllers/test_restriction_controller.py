from tensorhive.database import db_session
from tensorhive.models.Restriction import Restriction
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from sqlalchemy.orm.exc import NoResultFound
import auth_patcher
from importlib import reload

import datetime
import json
import pytest

ENDPOINT = BASE_URI + '/restrictions'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=False)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


# GET /restrictions
def test_get_all_restrictions_empty_response(tables, client):
    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 0


# GET /restrictions
def test_get_all_restrictions_with_data(tables, client):
    # Create new restriction and save it to the DB
    start_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    end_time = start_time + datetime.timedelta(hours=8)
    restriction = Restriction(name='TestRestriction', starts_at=start_time, ends_at=end_time, is_global=False)
    restriction.save()

    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 1


# GET /restrictions?user_id={id}
def test_get_user_restrictions(tables, client, new_user, restriction):
    new_user.save()
    restriction.apply_to_user(new_user)

    resp = client.get(ENDPOINT + '?user_id={}'.format(new_user.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?user_id={id}&include_user_groups=True
def test_get_users_group_restrictions(tables, client, new_group_with_member, restriction):
    new_group_with_member.save()
    restriction.apply_to_group(new_group_with_member)

    user = new_group_with_member.users[0]
    resp = client.get(ENDPOINT + '?user_id={}&include_user_groups=True'.format(user.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?group_id={id}
def test_get_group_restrictions(tables, client, new_group, restriction):
    new_group.save()
    restriction.apply_to_group(new_group)

    resp = client.get(ENDPOINT + '?group_id={}'.format(new_group.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?resource_id={id}
def test_get_resource_restrictions(tables, client, resource1, restriction):
    resource1.save()
    restriction.apply_to_resource(resource1)

    resp = client.get(ENDPOINT + '?resource_id={}'.format(resource1.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# GET /restrictions?schedule_id={id}
def test_get_schedule_restrictions(tables, client, active_schedule, restriction):
    active_schedule.save()
    restriction.add_schedule(active_schedule)

    resp = client.get(ENDPOINT + '?schedule_id={}'.format(active_schedule.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json[0]['id'] == restriction.id


# POST /restrictions - forbidden
def test_create_restriction_unprivileged(tables, client):
    data = {
        'name': 'Test restriction',
        'startsAt': '2100-01-01T10:00:00.000Z',
        'endsAt': '2101-02-01T10:00:00.000Z',
        'isGlobal': False
    }
    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.FORBIDDEN


# PUT /restrictions/{id} - update existing restriction - forbidden
def test_update_restriction_unprivileged(tables, client, restriction):
    restriction.save()
    new_name = 'Modified name'
    data = {
        'name': new_name
    }
    resp = client.put(ENDPOINT + '/' + str(restriction.id), headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.FORBIDDEN


# PUT /restrictions/{id}/groups/{group_id} - apply restriction to group - forbidden
def test_apply_restriction_to_group_unprivileged(tables, client, restriction, new_group):
    new_group.save()

    resp = client.put(ENDPOINT + '/{}/groups/{}'.format(restriction.id, new_group.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.FORBIDDEN


# DELETE /restrictions/{id}/hosts/{hostname}
def test_remove_resources_with_given_hostname_from_restriction(tables, client, restriction, resource1, resource2):
    resource1.hostname = 'nasa.gov'
    resource2.hostname = 'spacex.com'
    resource1.save()
    resource2.save()

    restriction.apply_to_resource(resource1)
    restriction.apply_to_resource(resource2)

    resp = client.delete(ENDPOINT + '/{}/hosts/{}'.format(restriction.id, resource1.hostname), headers=HEADERS)

    assert resp.status_code == HTTPStatus.FORBIDDEN


# DELETE /restriction/{id} - delete restriction
def test_delete_restriction_unprivileged(tables, client, restriction, new_user):
    new_user.save()
    restriction.apply_to_user(new_user)

    resp = client.delete(ENDPOINT + '/' + str(restriction.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.FORBIDDEN