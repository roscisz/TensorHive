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
            'description': 'testDescription',
            'userId': 1,
            'startAt': None,
            'stopAt': None}

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
    assert resp.status_code == HTTPStatus.NOT_FOUND  # checks if task from deleted job is deleted by cascade


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
