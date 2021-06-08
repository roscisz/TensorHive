from fixtures.controllers import API_URI as BASE_URI, HEADERS
from tensorhive.models.Job import Job
from tensorhive.models.Task import Task
from tensorhive.models.CommandSegment import CommandSegment2Task, CommandSegment
from http import HTTPStatus
import json
import auth_patcher
from importlib import reload

ENDPOINT = BASE_URI + '/tasks'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=True)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


# DELETE /tasks/{id}
def test_delete_not_owned_task(tables, client, new_admin_job):
    new_admin_job.save()
    task = new_admin_job.tasks[0]

    resp = client.delete(ENDPOINT + "/{}".format(task.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert len(Task.all()) == 0
    assert len(Job.all()) == 1
    assert len(CommandSegment.all()) == 0  # checks if segments from deleted task are deleted by cascade


# PUT /tasks/{id}
def test_update_not_owned_task(tables, client, new_admin_job):
    new_admin_job.save()
    task = new_admin_job.tasks[0]

    envs = [{
        'name': 'ENV',
        'value': 'path'
    }]
    params = [{
        'name': '--rank',
        'value': '3'
    }]
    data_to_update = {
        'hostname': 'remotehost',
        'cmdsegments': {
            'envs': envs,
            'params': params
        }
    }

    resp = client.put(ENDPOINT + '/{}'.format(task.id), headers=HEADERS, data=json.dumps(data_to_update))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['task']['hostname'] == 'remotehost'
    assert Task.get(int(resp_json['task']['id'])).number_of_params == 1
    assert Task.get(int(resp_json['task']['id'])).number_of_env_vars == 1
