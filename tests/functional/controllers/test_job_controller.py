from fixtures.models import new_job, new_task, new_user
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from tensorhive.models.Job import Job
from tensorhive.models.Task import Task
from tensorhive.models.CommandSegment import CommandSegment2Task, CommandSegment
from http import HTTPStatus

import json

ENDPOINT = BASE_URI + '/jobs'

# GET /jobs
def test_get_all_jobs(tables, client, new_job, new_user):
    new_user.save()
    resp = client.get(ENDPOINT + '?userId={}'.format(new_user.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['jobs']) == 0

    new_job.save()

    resp = client.get(ENDPOINT + '?userId={}'.format(new_user.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['jobs']) == 1
    
# POST /jobs
def test_create_job(tables, client):
    job_name = 'TestJob'
    data = {'name': job_name,
            'description' : 'testDescription',
            'userId' : 1}

    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['job']['id'] is not None
    assert resp_json['job']['name'] == job_name
    assert Job.get(int(resp_json['job']['id'])) is not None

# DELETE /jobs/{job_id}
def test_delete_job(tables, client, new_job, new_task):
    new_job.save()
    new_task.save()
    new_job.add_task(new_task)
    resp = client.get(ENDPOINT + '/{}/tasks'.format(new_job.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['tasks']) == 1

    resp = client.delete(ENDPOINT + '/{}'.format(new_job.id), headers=HEADERS)
        
    resp = client.get(ENDPOINT + '/{}/tasks'.format(new_job.id), headers=HEADERS)
    assert resp.status_code == HTTPStatus.NOT_FOUND # checks if task from deleted job is deleted by cascade

# GET /jobs/{job_id}/tasks
def test_get_tasks_from_job(tables, client, new_job, new_task):
    new_job.save()
    new_task.save()
    new_job.add_task(new_task)

    resp = client.get(ENDPOINT + '/{}/tasks'.format(new_job.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['tasks']) == 1

# PUT /jobs/{id}/tasks/{id}
def test_add_task_to_job(tables, client, new_job, new_task):
    new_job.save()
    new_task.save()

    resp = client.put(ENDPOINT + '/{}/tasks/{}'.format(new_job.id, new_task.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert new_job == new_task.job
    assert new_task in new_job.tasks

# DELETE /jobs/{id}/tasks/{id}
def test_remove_task_from_job(tables, client, new_job, new_task):
    new_job.save()
    new_task.save()
    new_job.add_task(new_task)

    resp = client.delete(ENDPOINT + '/{}/tasks/{}'.format(new_job.id, new_task.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert new_task.job == None
    assert len(new_job.tasks) == 0

# GET /jobs/{id}/execute
def test_execute_job(tables, client, new_job, new_user, new_task):
    new_user.save()
    new_job.save()
    new_task.save()
    new_job.add_task(new_task)

    resp = client.get(ENDPOINT + '/{}/execute'.format(new_job.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY # spawning tasks unsuccessful beacuse of test environment (synchronization)
    assert resp_json['not_spawned_list'] == [1] # id of a task that didn't spawn successfully

# POST /jobs/{job_id}/tasks
def test_create_task(tables, client, new_job):
    new_job.save()
    command = 'ENV= python command.py --batch_size 32 --rank 2'
    data = {'command': command,
            'hostname' : 'localhost'}

    resp = client.post(ENDPOINT + '/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
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
            'hostname' : 'localhost'}
    data2 = {'command': 'ENV= python command.py --batch_size 32',
            'hostname' : 'localhost'}

    resp = client.post(ENDPOINT + '/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data1))
    resp_json = json.loads(resp.data.decode('utf-8'))
    client.post(ENDPOINT + '/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data2))

    resp = client.delete(BASE_URI + '/tasks/{}'.format(resp_json['task']['id']), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(Task.all()) == 1
    assert len(Job.all()) == 1    
    assert len(CommandSegment.all()) == 3 # checks if segments from deleted task are deleted by cascade

# PUT /tasks/{id}
def test_update_task(tables, client, new_job, new_task):
    new_job.save()
    data_to_update = {'hostname' : 'remotehost',
            'cmd_segment_1': {'name' : '--batch_size',
                            'mode' : 'remove'},
            'cmd_segment_2': {'name' : '--rank',
                            'mode' : 'update',
                            'value' : '3'},                
            }

    data_to_post = {'command': 'ENV= python command.py --batch_size 32 --rank=1',
            'hostname' : 'localhost'}

    resp = client.post(ENDPOINT + '/{}/tasks'.format(new_job.id), headers=HEADERS, data=json.dumps(data_to_post))
    resp_json = json.loads(resp.data.decode('utf-8'))

    resp = client.put(BASE_URI + '/tasks/{}'.format(resp_json['task']['id']), headers=HEADERS, data=json.dumps(data_to_update))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert resp_json['task']['hostname'] == 'remotehost'
    assert resp_json['task']['command'] == 'ENV= python command.py --rank=3'