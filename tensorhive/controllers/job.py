import logging
from http import HTTPStatus
from typing import Any, Dict, List, Tuple, Optional
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
#from tensorhive.exceptions.InvalidRequestException import InvalidRequestException
from tensorhive.models.Job import Job
from tensorhive.models.Task import Task

log = logging.getLogger(__name__)
JOB = API.RESPONSES['job']
TASK = API.RESPONSES['task']
GENERAL = API.RESPONSES['general']

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
TaskId = int
JobId = int

# TODO May want to move to utils
def is_admin():
    claims = get_jwt_claims()
    return 'admin' in claims['roles']

@jwt_required
def get_by_id(id: JobId) -> Tuple[Content, HttpStatusCode]:
    try:
        job = Job.get(id)
        assert get_jwt_identity() == job.user_id or is_admin()
    except NoResultFound as e:
        log.warning(e)
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': GENERAL['unpriviliged']}, HTTPStatus.FORBIDDEN.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['get']['success'], 'job': job.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status

#TODO ADD SYNCHRONIZATION ?? 
@jwt_required
def get_all(userId: Optional[int]) -> Tuple[Content, HttpStatusCode]:
    user_id = userId
    try:
        if user_id:
            # Owner or admin can fetch
            assert get_jwt_identity() == user_id or is_admin()
            jobs = Job.query.filter(Job.user_id == user_id).all()
        else:
            # Only admin can fetch all
            assert is_admin()
            jobs = Job.all()
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': GENERAL['unpriviliged']}, HTTPStatus.FORBIDDEN.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        results = []
        for job in jobs:
            results.append(job.as_dict)
        content, status = {'msg': JOB['all']['success'], 'jobs': results}, HTTPStatus.OK.value
    finally:
        return content, status

#TODO assertions
@jwt_required
def create(job: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        new_job = Job(
            name=job['name'],
            description=job['description'],
            user_id=job['userId'],
            status=job['status'],
            _start_at=DateUtils.try_parse_string(job.get('startAt')),
            _end_at=DateUtils.try_parse_string(job.get('endAt'))
            )
        new_job.save()
    except ValueError:
        # Invalid string format for datetime
        content, status = {'msg': GENERAL['bad_request']}, HTTPStatus.UNPROCESSABLE_ENTITY.value
    except KeyError as e:
        # At least one of required fields was not present
        content = {'msg': JOB['create']['failure']['invalid'].format(reason=e)}
        status = HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content = {
            'msg': JOB['create']['success'],
            'job': new_job.as_dict
        }
        status = HTTPStatus.CREATED.value
    finally:
        return content, status


@jwt_required
def update(id: JobId, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    new_values = newValues
    allowed_fields = {'name', 'description', 'status', 'startAt', 'endAt'}
    try:
        job = Job.get(id)
        assert job.user_id == get_jwt_identity(), 'Not an owner'
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'

        for field_name, new_value in new_values.items():
            assert hasattr(job, field_name), 'job has no {} field'.format(field_name)
            setattr(job, field_name, new_value)
        job.save()
    except NoResultFound:
        content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': JOB['update']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['update']['success'], 'job': job.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status


@jwt_required
def delete(id: JobId) -> Tuple[Content, HttpStatusCode]:
    try:
        job = Job.get(id)
        assert job.user_id == get_jwt_identity(), 'Not an owner'
        job.destroy()
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


@jwt_required
def add_task(job_id: JobId, task_id: TaskId) -> Tuple[Content, HttpStatusCode]:
    job = None
    try:
        job = Job.get(job_id)
        task = Task.get(task_id)
        assert job.get('userId') == get_jwt_identity(), 'Not an owner'
        job.add_task(task)
    except NoResultFound:
        if job is None:
            content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': TASK['not_found']}, HTTPStatus.NOT_FOUND.value
#    except InvalidRequestException as e:
#        content, status = {'msg': JOB['tasks']['add']['failure']['duplicate'].format(reason=e)}, HTTPStatus.CONFLICT.value
    except AssertionError as e:
        content, status = {'msg': JOB['tasks']['add']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['tasks']['add']['success'], 'job': job.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status

@jwt_required
def remove_task(ob_id: JobId, task_id: TaskId) -> Tuple[Content, HttpStatusCode]:
    job = None
    try:
        job = Job.get(job_id)
        task = Task.get(task_id)
        assert job.get('userId') == get_jwt_identity(), 'Not an owner'
        job.remove_task(task)
    except NoResultFound:
        if job is None:
            content, status = {'msg': JOB['not_found']}, HTTPStatus.NOT_FOUND.value
        else:
            content, status = {'msg': TASK['not_found']}, HTTPStatus.NOT_FOUND.value
#    except InvalidRequestException as e:
#        content, status = {'msg': JOB['tasks']['remove']['failure']['not_found'].format(reason=e)}, HTTPStatus.NOT_FOUND.value
    except AssertionError as e:
        content, status = {'msg': JOB['tasks']['remove']['failure']['assertions'].format(reason=e)}, \
            HTTPStatus.UNPROCESSABLE_ENTITY.value
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, HTTPStatus.INTERNAL_SERVER_ERROR.value
    else:
        content, status = {'msg': JOB['tasks']['remove']['success'], 'job': job.as_dict}, HTTPStatus.OK.value
    finally:
        return content, status