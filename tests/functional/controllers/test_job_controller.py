from fixtures.controllers import API_URI as BASE_URI, HEADERS
from tensorhive.models.Job import Job
from tensorhive.models.Task import Task
from tensorhive.models.CommandSegment import CommandSegment2Task, CommandSegment
from http import HTTPStatus
from importlib import reload
import auth_patcher
import datetime
from datetime import timedelta
from tensorhive.utils.DateUtils import DateUtils
from tensorhive.models.Job import JobStatus

import json

ENDPOINT = BASE_URI + '/jobs'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=False)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


# GET /jobs
def test_get_all_jobs(tables, client, new_job, new_admin_job):
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
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=10))}

    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['job']['id'] is not None
    assert resp_json['job']['name'] == job_name
    assert Job.get(int(resp_json['job']['id'])) is not None


# POST /jobs
def test_create_job_without_dates(tables, client, new_user):
    new_user.save()
    job_name = 'TestJob'
    data = {'name': job_name,
            'description': 'testDescription',
            'userId': 1}

    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.CREATED
    assert resp_json['job']['id'] is not None
    assert resp_json['job']['name'] == job_name
    assert Job.get(int(resp_json['job']['id'])) is not None


# POST /jobs
def test_create_job_in_the_past(tables, client, new_user):
    new_user.save()
    job_name = 'TestJob'
    data = {'name': job_name,
            'description': 'testDescription',
            'userId': 1,
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() - timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=10))}

    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# POST /jobs
def test_create_job_that_stops_before_it_starts(tables, client, new_user):
    new_user.save()
    job_name = 'TestJob'
    data = {'name': job_name,
            'description': 'testDescription',
            'userId': 1,
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=4))}

    resp = client.post(ENDPOINT, headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# PUT /jobs/{job_id}
def test_update_job(tables, client, new_job):
    new_job.save()
    data = {'name': 'NewName',
            'description': 'NewDescription',
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=10)),
            }
    resp = client.put(ENDPOINT + '/{}'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.OK


# PUT /jobs/{job_id}
def test_update_job_without_dates(tables, client, new_job):
    new_job.save()
    data = {'name': 'NewName',
            'description': 'NewDescription'}
    resp = client.put(ENDPOINT + '/{}'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.OK


# PUT /jobs/{job_id}
def test_update_running_job(tables, client, new_job):
    new_job._status = JobStatus.running
    new_job.save()
    data = {'name': 'NewName',
            'description': 'NewDescription',
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=10)),
            }
    resp = client.put(ENDPOINT + '/{}'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# PUT /jobs/{job_id}
def test_update_not_owned_job(tables, client, new_admin_job):
    new_admin_job.save()
    data = {'name': 'NewName',
            'description': 'NewDescription',
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=10)),
            }
    resp = client.put(ENDPOINT + '/{}'.format(new_admin_job.id), headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.FORBIDDEN


# PUT /jobs/{job_id}
def test_update_job_to_start_in_the_past(tables, client, new_job):
    new_job._status = JobStatus.running
    new_job.save()
    data = {'name': 'NewName',
            'description': 'NewDescription',
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() - timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=10)),
            }
    resp = client.put(ENDPOINT + '/{}'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# PUT /jobs/{job_id}
def test_update_job_to_stop_before_start(tables, client, new_job):
    new_job._status = JobStatus.running
    new_job.save()
    data = {'name': 'NewName',
            'description': 'NewDescription',
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() - timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() - timedelta(hours=10)),
            }
    resp = client.put(ENDPOINT + '/{}'.format(new_job.id), headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


# DELETE /jobs/{job_id}
def test_delete_job(tables, client, new_job_with_task):
    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_job_with_task.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['tasks']) == 1

    resp = client.delete(ENDPOINT + '/{}'.format(new_job_with_task.id), headers=HEADERS)

    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_job_with_task.id), headers=HEADERS)
    assert resp.status_code == HTTPStatus.NOT_FOUND  # checks if task from deleted job is deleted by cascade


# DELETE /jobs/{job_id}
def test_delete_not_owned_job(tables, client, new_admin_job):
    resp = client.delete(ENDPOINT + '/{}'.format(new_admin_job.id), headers=HEADERS)
    assert resp.status_code == HTTPStatus.FORBIDDEN


# GET /tasks?job_id=1
def test_get_tasks_from_job(tables, client, new_job_with_task):
    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_job_with_task.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))

    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['tasks']) == 1


# GET /tasks?job_id=1
def test_get_tasks_from_not_owned_job(tables, client, new_admin_job):
    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_admin_job.id), headers=HEADERS)
    assert resp.status_code == HTTPStatus.FORBIDDEN


# PUT /jobs/{id}/tasks/{id}
def test_add_task_to_job(tables, client, new_job, new_task):
    resp = client.put(ENDPOINT + '/{}/tasks/{}'.format(new_job.id, new_task.id), headers=HEADERS)

    assert resp.status_code == HTTPStatus.OK
    assert new_job == new_task.job
    assert new_task in new_job.tasks
