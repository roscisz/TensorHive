from tensorhive.models.Group import Group
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from importlib import reload
import json
import auth_patcher
import tensorhive.controllers.group as sut

ENDPOINT = BASE_URI + '/groups'


def setup_module(module):
    auth_patch = auth_patcher.get_patch(superuser=False)
    auth_patch.start()
    reload(sut)
    auth_patch.stop()


# POST /groups
def test_create_unprivileged(tables, client):
    group_name = 'TestGroup'
    data = {'name': group_name}

    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))

    assert resp.status_code == HTTPStatus.FORBIDDEN


# GET /groups
def test_get_list_of_groups(tables, client):
    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 0  # no groups added yet


def test_get_list_of_groups_one_group_returned(tables, client, new_group):
    new_group.save()

    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert len(resp_json) == 1  # one group added already


# GET /groups/{id}
def test_get_group_by_id(tables, client, new_group):
    new_group.save()

    # Now try getting it
    resp = client.get(ENDPOINT + '/' + str(new_group.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json['group']['id'] == new_group.id
    assert resp_json['group']['name'] == new_group.name


# GET /groups/{id} - nonexistent id
def test_get_group_by_id_that_doesnt_exist(tables, client):
    non_existent_id = '777'
    resp = client.get(ENDPOINT + '/' + non_existent_id, headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# GET /groups?only_default=true - one default group
def test_get_default_groups(tables, client, new_group):
    new_group.is_default = True
    new_group.save()

    another_group = Group(name='Not a default group')
    another_group.save()

    resp = client.get(ENDPOINT + '?only_default=true', headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 1
    assert resp_json[0]['id'] == new_group.id


# GET /groups?only_default=true - when default group doesn't exist
def test_get_default_groups_when_no_default_group_exists(tables, client, new_group):
    new_group.save()

    resp = client.get(ENDPOINT + '?only_default=true', headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json) == 0
