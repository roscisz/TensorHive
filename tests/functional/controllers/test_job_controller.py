from fixtures.models import new_job, new_task
from fixtures.controllers import API_URI as BASE_URI, HEADERS
from tensorhive.models.Job import Job
from http import HTTPStatus

import json

ENDPOINT = BASE_URI + '/jobs'


# POST /jobs
def test_create(tables, client):
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

# PUT /jobs/{id}/tasks/{id}
def test_add_task_to_job(tables, client, new_job, new_task):
    new_job.save()
    new_task.save()

    resp = client.put(ENDPOINT + '/{}/tasks/{}'.format(new_job.id, new_task.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert new_job == new_task.job
    assert new_task in new_job.tasks

# GET /jobs
def test_get_all_jobs(tables, client, new_job):
    resp = client.get(ENDPOINT + '?userId=1', headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['jobs']) == 0

    new_job.save()

    resp = client.get(ENDPOINT + '?userId=1', headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['jobs']) == 1