from fixtures.controllers import API_URI as BASE_URI, HEADERS
from tensorhive.models.Job import Job
from tensorhive.models.Task import Task
from tensorhive.models.CommandSegment import CommandSegment2Task, CommandSegment
from http import HTTPStatus

import json

ENDPOINT = BASE_URI + '/tasks'


# POST /jobs/{job_id}/tasks
def test_create_task(tables, client, new_job, new_user):
    new_user.save()
    new_job.save()
    envs = [
        {
            'name': 'ENV',
            'value': 'path'
        },
        {
            'name': 'LIBPATH',
            'value': 'some/path/2'
        }
    ]
    params = [
        {
            'name': '--batch_size',
            'value': '32'
        },
        {
            'name': '--rank',
            'value': '2'
        }
    ]
    data = {
        'command': 'python command.py',
        'hostname': 'localhost',
        'cmdsegments': {
            'envs': envs,
            'params': params
        }
    }

    resp = client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['task']['command'] == 'python command.py'
    assert resp_json['task']['jobId'] == new_job.id
    assert len(new_job.tasks) == 1
    assert Task.get(int(resp_json['task']['id'])).number_of_params == 2


# DELETE /tasks/{id}
def test_delete_task(tables, client, new_job, new_user):
    new_user.save()
    new_job.save()
    envs = [{
        'name': 'ENV',
        'value': 'path'
    }]
    params2 = [{
        'name': '--batch_size',
        'value': '32'
    }]
    params1 = [
        {
            'name': '--batch_size',
            'value': '32'
        },
        {
            'name': '--rank',
            'value': '2'
        }
    ]
    data1 = {
        'command': 'python command.py',
        'hostname': 'localhost',
        'cmdsegments': {
            'envs': envs,
            'params': params1
        }
    }
    data2 = {
        'command': 'python command.py',
        'hostname': 'localhost',
        'cmdsegments': {
            'envs': envs,
            'params': params2
        }
    }

    resp = client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data1))
    resp_json = json.loads(resp.data.decode('utf-8'))
    client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data2))

    resp = client.delete(ENDPOINT + '/{}'.format(resp_json['task']['id']), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(Task.all()) == 1
    assert len(Job.all()) == 1
    assert len(CommandSegment.all()) == 2  # checks if segments from deleted task are deleted by cascade


# PUT /tasks/{id}
def test_update_task(tables, client, new_job, new_task, new_user):
    new_user.save()
    new_job.save()
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

    params_post = [
        {
            'name': '--batch_size',
            'value': '32'
        },
        {
            'name': '--rank',
            'value': '2'
        }
    ]
    data_to_post = {
        'command': 'python command.py',
        'hostname': 'localhost',
        'cmdsegments': {
            'envs': envs,
            'params': params_post
        }
    }

    resp = client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data_to_post))
    resp_json = json.loads(resp.data.decode('utf-8'))

    resp = client.put(ENDPOINT + '/{}'.format(resp_json['task']['id']),
                      headers=HEADERS, data=json.dumps(data_to_update))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['task']['hostname'] == 'remotehost'
    assert Task.get(int(resp_json['task']['id'])).number_of_params == 1
    assert Task.get(int(resp_json['task']['id'])).number_of_env_vars == 1
