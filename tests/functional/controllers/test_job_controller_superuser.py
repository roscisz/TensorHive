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

import json

ENDPOINT = BASE_URI + '/jobs'


def setup_module(_):
    auth_patches = auth_patcher.get_patches(superuser=True)
    for auth_patch in auth_patches:
        auth_patch.start()
    for module in auth_patcher.CONTROLLER_MODULES:
        reload(module)
    for auth_patch in auth_patches:
        auth_patch.stop()


# GET /jobs
def test_get_all_jobs(tables, client, new_job, new_admin_job):
    resp = client.get(ENDPOINT, headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['jobs']) == 2

# PUT /jobs/{job_id}
def test_update_not_owned_job(tables, client, new_admin_job):
    new_admin_job.save()
    data = {'name': 'NewName',
            'description': 'NewDescription',
            'startAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=5)),
            'stopAt': DateUtils.stringify_datetime_to_api_format(datetime.datetime.utcnow() + timedelta(hours=10)),
            }
    resp = client.put(ENDPOINT + '/{}'.format(new_admin_job.id), headers=HEADERS, data=json.dumps(data))
    assert resp.status_code == HTTPStatus.OK

# DELETE /jobs/{job_id}
def test_delete_not_owned_job(tables, client, new_admin_job):
    resp = client.delete(ENDPOINT + '/{}'.format(new_admin_job.id), headers=HEADERS)
    assert resp.status_code == HTTPStatus.OK
    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_admin_job.id), headers=HEADERS)
    assert resp.status_code == HTTPStatus.NOT_FOUND  # checks if task from deleted job is deleted by cascade


# GET /tasks?job_id=1
def test_get_tasks_from_not_owned_job(tables, client, new_admin_job):
    resp = client.get(BASE_URI + '/tasks?jobId={}'.format(new_admin_job.id), headers=HEADERS)
    resp_json = json.loads(resp.data.decode('utf-8'))
    assert resp.status_code == HTTPStatus.OK
    assert len(resp_json['tasks']) == 1
