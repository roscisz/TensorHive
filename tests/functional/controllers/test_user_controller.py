from tensorhive.models.Group import Group
from tensorhive.models.User import User
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus

import json

ENDPOINT = BASE_URI + '/user'


# POST /user/create - user gets added to a default group if it exists
def test_on_signup_user_gets_added_to_a_default_group(tables, client, new_group):
    new_group.save()
    Group.set_default_group(new_group.id)

    data = {
        'email': 'dummy@email.com',
        'username': 'Jacek',
        'password': 'notreallysafe'
    }
    resp = client.post(ENDPOINT + '/create', data=json.dumps(data), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert len(resp_json['user']['groups']) == 1
    assert resp_json['user']['groups'][0]['id'] == new_group.id
    assert new_group in User.get(resp_json['user']['id']).groups


# POST /user/create - user doesn't belong to any groups if no default group exists
def test_on_signup_user_does_not_belong_to_any_group_if_no_default_group_exists(tables, client, new_group):
    new_group.save()

    data = {
        'email': 'dummy@email.com',
        'username': 'Jacek',
        'password': 'notreallysafe'
    }
    resp = client.post(ENDPOINT + '/create', data=json.dumps(data), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert len(resp_json['user']['groups']) == 0
    assert len(User.get(resp_json['user']['id']).groups) == 0
