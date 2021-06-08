import logging
from http import HTTPStatus
from typing import Any, Dict, Tuple, Optional
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
from tensorhive.models.Job import Job, JobStatus
from tensorhive.models.Task import Task
from tensorhive.controllers.task import business_spawn, business_terminate, synchronize
from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from stringcase import snakecase
from tensorhive.exceptions.ForbiddenException import ForbiddenException

log = logging.getLogger(__name__)
JOB = API.RESPONSES['job']
TASK = API.RESPONSES['task']
GENERAL = API.RESPONSES['general']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
TaskId = int
JobId = int


# GET /jobs/{id}
@jwt_required
def get_by_id(id: JobId) -> Tuple[Content, HttpStatusCode]:
    """Fetches one Job db record"""
    try:
        job = Job.get(id)
        assert get_jwt_identity() == job.user_id or is_admin()
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, HTTPStatus.FORBIDDEN.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['get']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


# GET /jobs
@jwt_required
def get_all(userId: Optional[int]) -> Tuple[Content, HttpStatusCode]:
    """Fetches all Job records"""
    user_id = userId
    sync_all = True
    try:
        if user_id:
            # Owner or admin can fetch
            if not (is_admin() or get_jwt_identity() == user_id):
                raise ForbiddenException("not an owner")
            jobs = Job.query.filter(Job.user_id == user_id).all()
        else:
            # Only admin can fetch all
            if not is_admin():
                raise ForbiddenException("unauthorized")
            jobs = Job.all()
        if sync_all:
            for job in jobs:
                for task in job.tasks:
                    synchronize(task.id)
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except ForbiddenException as fe:
        content, status = {'msg': JOB['all']['forbidden'].format(reason=fe)}, HTTPStatus.FORBIDDEN.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        results = []
        for job in jobs:
            results.append(job.as_dict())
        content, status = {'msg': JOB['all']['success'], 'jobs': results}, HTTPStatus.OK.value
    finally:
        return content, status


# POST /jobs
@jwt_required
def create(job: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    """ Creates new Job db record."""
    try:
        assert job['userId'] == get_jwt_identity(), 'Not an owner'
        new_job = Job(
            name=job['name'],
            description=job['description'],
            user_id=job['userId']
        )
        if 'startAt' in job and job['startAt'] is not None:
            setattr(new_job, 'start_at', job['startAt'])
        if 'stopAt' in job and job['stopAt'] is not None:
            setattr(new_job, 'stop_at', job['stopAt'])
        new_job.save()
    except AssertionError as e:
        if e.args[0] == 'Not an owner':
            content, status = {'msg': GENERAL['unprivileged']}, HTTPStatus.FORBIDDEN.value
        else:
            content = {'msg': JOB['create']['failure']['invalid'].format(reason=e)}
            status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except ValueError:
        # Invalid string format for datetime
        content = {'msg': JOB['create']['failure']['invalid']}
        status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content = {
            'msg': JOB['create']['success'],
            'job': new_job.as_dict()
        }
        status = HTTPStatus.CREATED.value
    finally:
        return content, status


# PUT /jobs/{id}
@jwt_required
def update(id: JobId, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    """Updates certain fields of a Job db record, see `allowed_fields`."""
    new_values = newValues
    allowed_fields = {'name', 'description', 'startAt', 'stopAt'}
    try:
        job = Job.get(id)

        if not (is_admin() or job.user_id == get_jwt_identity()):
            raise ForbiddenException('not an owner')

        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'

        assert job.status is not JobStatus.running, 'must be stopped first'

        for field_name, new_value in new_values.items():
            field_name = snakecase(field_name)
            if new_value is not None:
                assert hasattr(job, field_name), 'job has no {} field'.format(field_name)
                setattr(job, field_name, new_value)
        job.save()
    except ForbiddenException as fe:
        content, status = {'msg': JOB['update']['failure']['forbidden'].format(reason=fe)}, 403
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': JOB['update']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['update']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


# DELETE /jobs/{id}
@jwt_required
def delete(id: JobId) -> Tuple[Content, HttpStatusCode]:
    """Deletes a Job db record.

    If running, requires stopping job manually in advance."""
    try:
        job = Job.get(id)

        if not (is_admin() or job.user_id == get_jwt_identity()):
            raise ForbiddenException('not an owner')

        assert job.status is not JobStatus.running, 'must be stopped first'
        job.destroy()
    except ForbiddenException as fe:
        content, status = {'msg': JOB['update']['failure']['forbidden'].format(reason=fe)}, 403
    except AssertionError as e:
        content, status = {'msg': JOB['delete']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['delete']['success']}, HTTPStatus.OK.value
    finally:
        return content, status


# PUT /jobs/{job_id}/task/{task_id}
@jwt_required
def add_task(job_id: JobId, task_id: TaskId) -> Tuple[Content, HttpStatusCode]:
    """Adds Task to a specific Job."""
    job = None
    try:
        job = Job.get(job_id)
        task = Task.get(task_id)
        assert job.user_id == get_jwt_identity(), 'Not an owner'
        job.add_task(task)
    except NoResultFound:
        if job is None:
            content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': TASK['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException as e:
        content, status = {'msg': JOB['tasks']['add']['failure']['duplicate'].format(reason=e)}, \
            HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': JOB['tasks']['add']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.FORBIDDEN.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['tasks']['add']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


# DELETE /jobs/{job_id}/task/{task_id}
@jwt_required
def remove_task(job_id: JobId, task_id: TaskId) -> Tuple[Content, HttpStatusCode]:
    """Removes Task from Job."""
    job = None
    try:
        job = Job.get(job_id)
        task = Task.get(task_id)
        assert job.user_id == get_jwt_identity(), 'Not an owner'
        job.remove_task(task)
    except NoResultFound:
        if job is None:
            content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': TASK['not_found']}, HTTPStatus.NOT_FOUND.value
    except InvalidRequestException as e:
        content, status = {'msg': JOB['tasks']['remove']['failure']['not_found'].format(reason=e)}, \
            HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': JOB['tasks']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.FORBIDDEN.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['tasks']['remove']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


# GET /jobs/{id}/execute
@jwt_required
def execute(id: JobId) -> Tuple[Content, HttpStatusCode]:
    try:
        job = Job.get(id)
        assert job.user_id == get_jwt_identity(), 'Not an owner'
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': GENERAL['unprivileged'].format(reason=e)}, HTTPStatus.FORBIDDEN.value
    else:
        content, status = business_execute(id)
    finally:
        return content, status


def business_execute(id: JobId) -> Tuple[Content, HttpStatusCode]:
    """Tries to spawn all commands stored in Tasks belonging to Job (db records - (task.command))

    It won't allow for executing job which is currently running.
    If execute operation has succeeded then `running` status is set

    If one or more tasks did not spawn correctly, job is marked as running anyway and
    tasks which spawned correctly are running too. In that case user can stop the job and
    try to run it again, or just continue.
    """
    try:
        not_spawned_tasks = []
        job = Job.get(id)
        assert job.status is not JobStatus.running, 'Job is already running'
        for task in job.tasks:
            content, status = business_spawn(task.id)
            if status is not HTTPStatus.OK.value:
                not_spawned_tasks.append(task.id)

        job.synchronize_status()
        job.save()

        assert not_spawned_tasks == [], 'Could not spawn some tasks'

        # If job was scheduled to stop and user just
        # execute that job manually, scheduler should still
        # continue to watch and stop the job automatically.
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        if 'Job is already running' in e.args[0]:
            content, status = {'msg': JOB['execute']['failure']['state'].format(reason=e)}, \
                HTTPStatus.CONFLICT.value
        else:
            content, status = {'msg': JOB['execute']['failure']['tasks'].format(reason=e),
                               'not_spawned_list': not_spawned_tasks}, HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        log.info('Job {} is now: {}'.format(job.id, job.status.name))
        content, status = {'msg': JOB['execute']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


# PUT /jobs/{id}/enqueue
@jwt_required
def enqueue(id: JobId) -> Tuple[Content, HttpStatusCode]:
    try:
        job = Job.get(id)
        if not (is_admin() or job.user_id == get_jwt_identity()):
            raise ForbiddenException("not an owner")
        job.enqueue()
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except ForbiddenException as fe:
        content, status = {'msg': GENERAL['unprivileged'].format(reason=fe)}, HTTPStatus.FORBIDDEN.value
    except AssertionError as ae:
        content, status = {'msg': JOB['enqueue']['failure'].format(reason=ae)}, HTTPStatus.CONFLICT.value
    else:
        content, status = {'msg': JOB['enqueue']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


# PUT /jobs/{id}/dequeue
@jwt_required
def dequeue(id: JobId) -> Tuple[Content, HttpStatusCode]:
    try:
        job = Job.get(id)
        if not (is_admin() or job.user_id == get_jwt_identity()):
            raise ForbiddenException("not an owner")
        job.dequeue()
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except ForbiddenException as fe:
        content, status = {'msg': GENERAL['unprivileged'].format(reason=fe)}, HTTPStatus.FORBIDDEN.value
    except AssertionError as ae:
        content, status = {'msg': JOB['dequeue']['failure'].format(reason=ae)}, HTTPStatus.CONFLICT.value
    else:
        content, status = {'msg': JOB['dequeue']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


# GET /jobs/{id}/stop
@jwt_required
def stop(id: JobId, gracefully: Optional[bool] = True) -> Tuple[Content, HttpStatusCode]:
    try:
        job = Job.get(id)
        assert get_jwt_identity() == job.user_id or is_admin()
        assert job.status is JobStatus.running, 'Only running jobs can be stopped'
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        if 'Only running jobs can be stopped' in e.args[0]:
            content, status = {'msg': JOB['stop']['failure']['state'].format(reason=e)}, \
                HTTPStatus.CONFLICT.value
        else:
            content, status = {'msg': GENERAL['unprivileged']}, HTTPStatus.FORBIDDEN.value
    else:
        content, status = business_stop(id, gracefully)
    finally:
        return content, status


def business_stop(id: JobId, gracefully: Optional[bool] = True) -> Tuple[Content, HttpStatusCode]:
    """Tries to terminate all Tasks belonging to Job.

    If some tasks did not terminate correctly, job is not terminated, but all of
    the other (correct) tasks are terminated.

    'gracefully' parameter is passed to all of Tasks 'terminate' methods to either send
    SIGINT (default) or SIGKILL to processes with pid that are stored in Tasks db records.

    In order to send SIGKILL, pass `gracefully=False` to `stop` function.

    Note that termination signal should be respected by most processes, however this
    function does not guarantee stoping them!
    """
    try:
        job = Job.get(id)
        not_terminated_tasks = 0
        for task in job.tasks:
            content, status = business_terminate(task.id, gracefully)
            if status != HTTPStatus.OK.value:
                not_terminated_tasks += 1

        assert not_terminated_tasks == 0, 'Not all tasks could be terminated'
        # If job was scheduled to start automatically
        # but user decided to stop it manually
        # scheduler should not execute the job by itself then
        if job.start_at:
            # So this job should not be started automatically anymore
            job.start_at = None
        job.synchronize_status()
        job.save()
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': JOB['stop']['failure']['tasks'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        log.info('Job {} is now: {}'.format(job.id, job.status.name))
        content, status = {'msg': JOB['stop']['success'], 'job': job.as_dict()}, HTTPStatus.OK.value
    finally:
        return content, status


def is_admin() -> bool:
    return 'admin' in get_jwt_claims()['roles']
