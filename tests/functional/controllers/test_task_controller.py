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
    command = 'ENV= python command.py --batch_size 32 --rank 2'
    data = {'command': command,
            'hostname': 'localhost'}

    resp = client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['task']['command'] == command
    assert resp_json['task']['jobId'] == new_job.id
    assert len(new_job.tasks) == 1
    assert Task.get(int(resp_json['task']['id'])).number_of_params == 2


# DELETE /tasks/{id}
def test_delete_task(tables, client, new_job, new_user):
    new_user.save()
    new_job.save()
    data1 = {'command': 'ENV= python command.py --batch_size 32 --rank=2',
             'hostname': 'localhost'}
    data2 = {'command': 'ENV= python command.py --batch_size 32',
             'hostname': 'localhost'}

    resp = client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data1))
    resp_json = json.loads(resp.data.decode('utf-8'))
    client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data2))

    resp = client.delete(ENDPOINT + '/{}'.format(resp_json['task']['id']), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(Task.all()) == 1
    assert len(Job.all()) == 1
    assert len(CommandSegment.all()) == 3  # checks if segments from deleted task are deleted by cascade


# PUT /tasks/{id}
def test_update_task(tables, client, new_job, new_task, new_user):
    new_user.save()
    new_job.save()
    data_to_update = {'hostname': 'remotehost',
                      'cmd_segment_1': {'name': '--batch_size',
                                        'mode': 'remove'},
                      'cmd_segment_2': {'name': '--rank',
                                        'mode': 'update',
                                        'value': '3'}}

    data_to_post = {'command': 'ENV= python command.py --batch_size 32 --rank=1',
                    'hostname': 'localhost'}

    resp = client.post(BASE_URI + '/jobs/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data_to_post))
    resp_json = json.loads(resp.data.decode('utf-8'))

    resp = client.put(ENDPOINT + '/{}'.format(resp_json['task']['id']),
                      headers=HEADERS, data=json.dumps(data_to_update))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['task']['hostname'] == 'remotehost'
    assert resp_json['task']['command'] == 'ENV= python command.py --rank=3'
