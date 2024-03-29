from tensorhive.models.Group import Group
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
from importlib import reload
import json
import auth_patcher


ENDPOINT = BASE_URI + '/groups'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=True)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


# POST /groups
def test_create_group(tables, client):
    group_name = 'TestGroup'
    data = {'name': group_name}

    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['group']['id'] is not None
    assert resp_json['group']['name'] == group_name
    assert Group.get(int(resp_json['group']['id'])) is not None


# PUT /groups/{id}
def test_update_group(tables, client, new_group):
    new_group.save()

    new_group_name = new_group.name + '111'
    resp = client.put(ENDPOINT + '/' + str(new_group.id), headers=HEADERS, data=json.dumps({'name': new_group_name}))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json['group']['name'] == new_group_name
    assert Group.get(new_group.id).name == new_group_name


# PUT /groups/{id} - nonexistent id
def test_update_group_that_doesnt_exist(tables, client):
    non_existent_id = '777'
    resp = client.put(ENDPOINT + '/' + non_existent_id, headers=HEADERS, data=json.dumps({'name': 'test'}))

    assert resp.status_code == HTTPStatus.NOT_FOUND


# DELETE /groups/{id}
def test_delete_group(tables, client, new_group):
    new_group.save()

    resp = client.delete(ENDPOINT + '/' + str(new_group.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK

    # Let's get all groups to verify
    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert len(resp_json) == 0


# DELETE /groups/{id} - nonexistent id
def test_delete_group_that_doesnt_exist(tables, client):
    non_existent_id = '777'
    resp = client.delete(ENDPOINT + '/' + non_existent_id, headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /groups/{id}/users/{id}
def test_add_user_to_a_group(tables, client, new_group, new_user):
    new_group.save()
    new_user.save()

    resp = client.put(ENDPOINT + '/{}/users/{}'.format(new_group.id, new_user.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert new_group in new_user.groups
    assert new_user in new_group.users


# DELETE /groups/{id}/users/{id}
def test_remove_user_from_a_group(tables, client, new_group_with_member):
    new_group_with_member.save()
    user = new_group_with_member.users[0]

    resp = client.delete(ENDPOINT + '/{}/users/{}'.format(new_group_with_member.id, user.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert new_group_with_member not in user.groups
    assert user not in new_group_with_member.users


# PUT /groups/{id}/users/{id} - nonexistent user id
def test_add_nonexistent_user_to_a_group(tables, client, new_group):
    new_group.save()
    nonexistent_user_id = '777'

    resp = client.put(ENDPOINT + '/{}/users/{}'.format(new_group.id, nonexistent_user_id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /groups/{id}/users/{id} - nonexistent group id
def test_add_user_to_nonexistent_group(tables, client, new_user):
    new_user.save()
    nonexistent_group_id = '777'

    resp = client.put(ENDPOINT + '/{}/users/{}'.format(nonexistent_group_id, new_user.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# DELETE /groups/{id}/users/{id} - nonexistent user id
def test_remove_nonexistent_user_from_a_group(tables, client, new_group):
    new_group.save()
    nonexistent_user_id = '777'

    resp = client.delete(ENDPOINT + '/{}/users/{}'.format(new_group.id, nonexistent_user_id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# DELETE /groups/{id}/users/{id} - nonexistent group id
def test_remove_user_from_a_nonexistent_group(tables, client, new_user):
    new_user.save()
    nonexistent_group_id = '777'

    resp = client.delete(ENDPOINT + '/{}/users/{}'.format(nonexistent_group_id, new_user.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.NOT_FOUND


# PUT /groups/{id}
def test_set_group_as_a_default(tables, client, new_group):
    new_group.save()

    resp = client.put(ENDPOINT + '/{}'.format(new_group.id), data=json.dumps({'isDefault': True}), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert Group.get(new_group.id).is_default


# PUT /groups/{id}
def test_mark_default_group_as_non_default(tables, client, new_group):
    new_group.is_default = True
    new_group.save()

    resp = client.put(ENDPOINT + '/{}'.format(new_group.id), data=json.dumps({'isDefault': False}),
                      headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert Group.get(new_group.id).is_default is False
