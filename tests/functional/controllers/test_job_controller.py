from fixtures.controllers import API_URI as BASE_URI, HEADERS
from tensorhive.models.Job import Job
from tensorhive.models.Task import Task
from tensorhive.models.CommandSegment import CommandSegment2Task, CommandSegment
from http import HTTPStatus

import json

ENDPOINT = BASE_URI + '/jobs'


# GET /jobs
def test_get_all_jobs(tables, client, new_job):
    user = new_job.user
    resp = client.get(ENDPOINT + '?userId={}'.format(user.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['jobs']) == 1


# POST /jobs
def test_create_job(tables, client, new_user):
    new_user.save()
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
def test_delete_job(tables, client, new_job_with_task):
    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_job_with_task.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['tasks']) == 1

    resp = client.delete(ENDPOINT + '/{}'.format(new_job_with_task.id), headers=HEADERS)

    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_job_with_task.id), headers=HEADERS)
    assert resp.status_code == HTTPStatus.NOT_FOUND  # checks if task from deleted job is deleted by cascade


# GET /tasks?job_id=1
def test_get_tasks_from_job(tables, client, new_job_with_task):
    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_job_with_task.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['tasks']) == 1


# PUT /jobs/{id}/tasks/{id}
def test_add_task_to_job(tables, client, new_job, new_task):
    resp = client.put(ENDPOINT + '/{}/tasks/{}'.format(new_job.id, new_task.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert new_job == new_task.job
    assert new_task in new_job.tasks
