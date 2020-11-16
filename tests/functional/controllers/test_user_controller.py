from tensorhive.models.Group import Group
from tensorhive.models.User import User
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from http import HTTPStatus
import auth_patcher
from importlib import reload

import json

ENDPOINT = BASE_URI + '/user'


def setup_module(_):
    auth_patch = auth_patcher.get_patch(superuser=False)
    auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    auth_patch.stop()


# POST /user/create - forbidden
def test_user_signup_unprivileged(tables, client):
    data = {
        'email': 'dummy@email.com',
        'username': 'Jacek',
        'password': 'notreallysafe'
    }
    resp = client.post(ENDPOINT + '/create', data=json.dumps(data), headers=HEADERS)

    assert resp.status_code == HTTPStatus.FORBIDDEN
