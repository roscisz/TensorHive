from tensorhive.models.Task import Task, TaskStatus
from tensorhive.models.User import User
from tensorhive.core import task_nursery
from tensorhive.utils.DateUtils import DateUtils
from tensorhive.core.task_nursery import SpawnError, ExitCodeError
from pssh.exceptions import ConnectionErrorException, AuthenticationException, UnknownHostException
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
from functools import wraps
from typing import Optional, Callable, Any, Dict, Tuple
from datetime import datetime, timedelta
from stringcase import snakecase
import logging

log = logging.getLogger(__name__)
TASK = API.RESPONSES['task']
SSH = API.RESPONSES['ssh']
SCREEN_SESSIONS = API.RESPONSES['screen-sessions']
GENERAL = API.RESPONSES['general']
"""
This module contains two kinds of controllers:
- production-ready with authorization and authentication
- unprotected core business logic that can be used anywhere

My goal was to separate authorization from controllers' logic, so that
manual and automatic testing doesn't require patching Flask context
(@jwt_required breaks a lot of things)

In before: some controller MUST have camelCased arguments in order to keep up with API.
They are aliased to snake_case immediately inside controller body.
Connexion has this feature under the hood but it does not always work as it should (only in simple cases)
"""

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
TaskId = int


def synchronize(task_id: TaskId) -> None:
    """Updates the state of a Task object stored in database.

    It compares current db record with list of active screen session (their pids in general)
    on node defined by that record (task.user.username@task.host).

    If task_nursery is unable to fetch active screen sessions then
    the new state is always set to unsynchronized.

    If task.pid is not alive (db record is outdated), then it
    makes transition from last known state to a new state:

    state before sync   => state applied after sync
    -----------------------------------------------
    running             => terminated
    unsynchronized      => not_running
    """
    log.debug('Syncing Task {}...'.format(task_id))
    try:
        task = Task.get(task_id)
        assert task.hostname, 'hostname is empty'
        assert task.user, 'user does not exist'
        active_sessions_pids = task_nursery.running(host=task.hostname, user=task.user.username)
    except NoResultFound:
        # This exception must be handled within try/except block when using Task.get()
        # In other words, methods decorated with @synchronize_task_record must handle this case by themselves!
        log.warning(
            'Task {} could not be found (also synchronized). Failing without taking any action...'.format(task_id))
        pass
    except (AssertionError, Exception) as e:
        # task_nursery.running pssh exceptions are also catched here
        log.error('Unable to synchronize Task {}, reason: {}'.format(task_id, e))
        log.debug('Task {} status was: {}'.format(task_id, task.status.name))
        task.status = TaskStatus.unsynchronized
        task.save()
        log.debug('Task {} is now: {}'.format(task_id, task.status.name))
    else:
        log.debug('[BEFORE SYNC] Task {} status was: {}'.format(task_id, task.status.name))
        change_status_msg = '[AFTER SYNC] Task {id} is now: {curr_status}'
        if task.pid not in active_sessions_pids:
            if task.status is TaskStatus.running:
                task.status = TaskStatus.terminated
                log.debug(change_status_msg.format(id=task_id, curr_status=task.status.name))
            if task.status is TaskStatus.unsynchronized:
                task.status = TaskStatus.not_running
                log.debug(change_status_msg.format(id=task_id, curr_status=task.status.name))
            task.pid = None
            task.save()


def synchronize_task_record(func: Callable) -> Callable:
    """Decorated function MUST CONTAIN task id (int), function can take more arguments though.

    In case when task.id could not be obtained from wrapped function's arguments,
    synchronization will be aborted, but it won't affect wrapped function (silent fail).
    """

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            task_id = args[0]
        except IndexError:
            task_id = kwargs.get('id') or kwargs.get('task_id') or kwargs.get('taskId')

        if task_id:
            synchronize(task_id)
        else:
            log.critical('Synchronization aborted!')
            log.critical('Task id not found in {}(), args: {}, kwargs: {}'.format(func.__name__, args, kwargs))
        return func(*args, **kwargs)

    return sync_wrapper


# Controllers
# POST /tasks
@jwt_required
def create(task: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        # User is not allowed to create task for someone else
        assert task.get('userId') == get_jwt_identity()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_create(task)
    finally:
        return content, status


# GET /tasks/{id}
@jwt_required
def get(id: TaskId) -> Tuple[Content, HttpStatusCode]:
    try:
        task = Task.get(id)
        assert get_jwt_identity() == task.user_id or is_admin()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_get(id)
    finally:
        return content, status


#  GET /tasks?userId=X?syncAll=1
@jwt_required
def get_all(userId: Optional[int], syncAll: Optional[bool]) -> Tuple[Content, HttpStatusCode]:
    user_id, sync_all = userId, syncAll
    try:
        if user_id:
            # Owner or admin can fetch
            assert get_jwt_identity() == user_id or is_admin()
        else:
            # Only admin can fetch all
            assert is_admin()

    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_get_all(user_id, sync_all)
    finally:
        return content, status


# PUT /tasks/{id}
@jwt_required
def update(id: TaskId, newValues: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    try:
        task = Task.get(id)
        assert task.user_id == get_jwt_identity(), 'Not an owner'
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_update(id, newValues)
    finally:
        return content, status


# DELETE /tasks/{id}
@jwt_required
def destroy(id: TaskId) -> Tuple[Content, HttpStatusCode]:
    try:
        task = Task.get(id)
        assert task.user_id == get_jwt_identity(), 'Not an owner'
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_destroy(id)
    finally:
        return content, status


# GET /tasks/{id}/spawn
@jwt_required
def spawn(id: TaskId) -> Tuple[Content, HttpStatusCode]:
    try:
        task = Task.get(id)
        assert task.user_id == get_jwt_identity(), 'Not an owner'
    except NoResultFound as e:
        log.error(e)
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_spawn(id)
    finally:
        return content, status


# GET /tasks/{id}/terminate
@jwt_required
def terminate(id: TaskId, gracefully: Optional[bool] = True) -> Tuple[Content, HttpStatusCode]:
    try:
        task = Task.get(id)
        assert get_jwt_identity() == task.user_id or is_admin()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_terminate(id, gracefully)
    finally:
        return content, status


# GET /tasks/{id}/log
@jwt_required
def get_log(id: TaskId, tail: bool) -> Tuple[Content, HttpStatusCode]:
    try:
        task = Task.get(id)
        assert get_jwt_identity() == task.user_id or is_admin()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError:
        content, status = {'msg': GENERAL['unprivileged']}, 403
    else:
        content, status = business_get_log(id, tail)
    finally:
        return content, status


# Business logic


def business_get_all(user_id: Optional[int], sync_all: Optional[bool]) -> Tuple[Content, HttpStatusCode]:
    """Fetches either all Task records or only those in relation with specific user.
    Allows for synchronizing state of each Task out-of-the-box.

    In typical scenario API client would want to get all records without sync and
    then run sync each records individually.
    """
    # TODO Exceptions should never occur, but need to experiment more
    if user_id:
        # Returns [] if such User with such id does not exist (SQLAlchemy behavior)
        tasks = Task.query.filter(Task.user_id == user_id).all()
    else:
        tasks = Task.all()

    # Wanted to decouple syncing from dict conversion with 2 oneliners (using list comprehension),
    # but this code is O(n) instead of O(2n)
    results = []
    for task in tasks:
        if sync_all:
            synchronize(task.id)
        results.append(task.as_dict())
    return {'msg': TASK['all']['success'], 'tasks': results}, 200


def business_create(task: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    """Creates new Task db record.
    Fields which require to be of datetime type are explicitly converted here.
    """
    try:
        new_task = Task(
            user_id=task['userId'],
            hostname=task['hostname'],
            command=task['command'],
            # TODO Adjust API spec, optional fields
            spawn_at=DateUtils.try_parse_string(task.get('spawnAt')),
            terminate_at=DateUtils.try_parse_string(task.get('terminateAt')))
        # assert all(task.values()), 'fields cannot be blank or null'
        new_task.save()
    except ValueError:
        # Invalid string format for datetime
        content, status = {'msg': GENERAL['bad_request']}, 422
    except KeyError:
        # At least one of required fields was not present
        content, status = {'msg': GENERAL['bad_request']}, 422
    except AssertionError as e:
        content, status = {'msg': TASK['create']['failure']['invalid'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        content, status = {'msg': TASK['create']['success'], 'task': new_task.as_dict()}, 201
    finally:
        return content, status


@synchronize_task_record
def business_get(id: TaskId) -> Tuple[Content, HttpStatusCode]:
    """Fetches one Task db record"""
    try:
        task = Task.get(id)
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        content, status = {'msg': TASK['get']['success'], 'task': task.as_dict()}, 200
    finally:
        return content, status


# TODO What if task is already running: allow for updating command, hostname, etc.?
def business_update(id: TaskId, new_values: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    """Updates certain fields of a Task db record, see `allowed_fields`."""
    allowed_fields = {'command', 'hostname', 'spawnAt', 'terminateAt'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        task = Task.get(id)
        for field_name, new_value in new_values.items():
            if field_name in {'spawnAt', 'terminateAt'}:
                new_value = DateUtils.try_parse_string(new_value)
            field_name = snakecase(field_name)
            # Check that every field matches
            assert (field_name is not None) and hasattr(task, field_name), 'task has no {} field'.format(field_name)
            setattr(task, field_name, new_value)
        task.save()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except ValueError:
        # Invalid string format for datetime
        content, status = {'msg': GENERAL['bad_request']}, 422
    except AssertionError as e:
        content, status = {'msg': TASK['update']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        content, status = {'msg': TASK['update']['success'], 'task': task.as_dict()}, 201
    finally:
        return content, status


@synchronize_task_record
def business_destroy(id: TaskId) -> Tuple[Content, HttpStatusCode]:
    """Deletes a Task db record. Requires terminating task manually in advance."""
    try:
        task = Task.get(id)
        assert task.status is not TaskStatus.running, 'must be terminated first'
        task.destroy()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': TASK['delete']['failure']['assertions'].format(reason=e)}, 422
    except Exception:
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        content, status = {'msg': TASK['delete']['success']}, 200
    finally:
        return content, status


# TODO Disable this endpoint later, return 403 Forbidden
# GET /screen-sessions?username=foo&hostname=bar
def screen_sessions(username: str, hostname: str) -> Tuple[Content, HttpStatusCode]:
    """Returns pids of running `screen` sessions.

    This endpoint is for purely development purposes,
    currently there's no need to use it.
    """
    try:
        assert username and hostname, 'parameters must not be empty'
        pids = task_nursery.running(host=hostname, user=username)
    except AssertionError as e:
        content, status = {'msg': SCREEN_SESSIONS['failure']['assertions'].format(reason=e)}, 422
    except (ConnectionErrorException, AuthenticationException, UnknownHostException) as e:
        content, status = {'msg': SSH['failure']['connection'].format(reason=e)}, 500
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        # FIXME
        content, status = {'msg': SCREEN_SESSIONS['success'], 'pids': pids}, 200
    finally:
        return content, status


@synchronize_task_record
def business_spawn(id: TaskId) -> Tuple[Content, HttpStatusCode]:
    """Spawns command stored in Task db record (task.command).

    It won't allow for spawning task which is currently running (sync + status check).
    If spawn operation has succeeded then `running` status is set.
    """
    try:
        task = Task.get(id)

        assert task.status is not TaskStatus.running, 'task is already running'
        assert task.command, 'command is empty'
        assert task.hostname, 'hostname is empty'
        assert task.user, 'user does not exist'

        pid = task_nursery.spawn(task.command, task.hostname, task.user.username, name_appendix=str(task.id))
        task.pid = pid
        task.status = TaskStatus.running

        # If task was scheduled to terminate and user just
        # spawned that task manually, scheduler should still
        # continue to watch and terminate the task automatically.
        task.save()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': TASK['spawn']['failure']['assertions'].format(reason=e)}, 422
    except SpawnError as e:
        log.warning(e)
        content, status = {'msg': TASK['spawn']['failure']['backend'].format(reason=e)}, 500
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        log.info('Task {} is now: {}'.format(task.id, task.status.name))
        content, status = {'msg': TASK['spawn']['success'], 'pid': pid}, 200
    finally:
        return content, status


@synchronize_task_record
def business_terminate(id: TaskId, gracefully: Optional[bool] = True) -> Tuple[Content, HttpStatusCode]:
    """Sends SIGINT (default) or SIGKILL to process with pid that is stored in Task db record.

    In order to send SIGKILL, pass `gracefully=False` to `terminate` function.
    Note that:
    1) `exit_code` is related to executing kill operation, not killed process.
    2) termination signal should be respected by most processes, however this
        function does not guarantee stoping the process!
    """
    try:
        task = Task.get(id)
        assert task.status is TaskStatus.running, 'only running tasks can be terminated'
        assert task.pid, 'task has no pid assigned'  # It means there's inconsistency

        # gracefully:
        # True -> interrupt (allows output to be flushed into log file)
        # None -> terminate (works almost every time, but losing output that could be produced before closing)
        # False -> kill (similar to above, but success is almost guaranteed)
        exit_code = task_nursery.terminate(task.pid, task.hostname, task.user.username, gracefully=gracefully)

        if exit_code != 0:
            raise ExitCodeError('operation exit code is not 0')

        # Note: Code below is unsafe, because interrupt and terminate does not guarantee success.
        # It's better to let synchhronization update this (via comparison with screen sessions)
        # (Unsafe section) Original comment: Allow to spawn that task again
        # task.pid = None
        # task.status = TaskStatus.terminated

        # Task was scheduled to spawn automatically
        # but user decided to terminate it manually
        # scheduler should not spawn the task by itself then
        if task.spawn_at:
            # So this task should not be spawned automatically anymore
            task.spawn_at = None
            task.save()
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': TASK['terminate']['failure']['state'].format(reason=e)}, 409
    except ExitCodeError:
        content, status = {'msg': TASK['terminate']['failure']['exit_code'], 'exit_code': exit_code}, 202
    # TODO What if terminate could not connect, ConnectionErrorException?
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        content, status = {'msg': TASK['terminate']['success'], 'exit_code': exit_code}, 200
    finally:
        return content, status


def business_get_log(id: TaskId, tail: bool) -> Tuple[Content, HttpStatusCode]:
    """Fetches log file created by spawned task (output redirection).

    It relies on reading files located on filesystem, via connection with `task.user.username@task.host`
    If file does not exist there's no way to fetch it from database (currently).
    File names must be named in one fashion (standard defined in `task_nursery.fetch_log`,
    currently: `task_<id>.log`). Renaming them manually will lead to inconsistency or 'Not Found' errors.

    `tail` argument allows for returning only the last few lines (10 is default for `tail` program).
    For more details, see,: `task_nursery.fetch_log`.
    """
    try:
        task = Task.get(id)
        assert task.hostname, 'hostname is empty'
        assert task.user, 'user does not exist'
        output_gen, log_path = task_nursery.fetch_log(task.hostname, task.user.username, task.id, tail)
    except NoResultFound:
        content, status = {'msg': TASK['not_found']}, 404
    except ExitCodeError as e:
        content, status = {'msg': TASK['get_log']['failure']['not_found'].format(location=e)}, 404
    except AssertionError as e:
        content, status = {'msg': TASK['get_log']['failure']['assertions'].format(reason=e)}, 422
    except (ConnectionErrorException, AuthenticationException, UnknownHostException) as e:
        content, status = {'msg': SSH['failure']['connection'].format(reason=e)}, 500
    except Exception as e:
        log.critical(e)
        content, status = {'msg': GENERAL['internal_error']}, 500
    else:
        content, status = {'msg': TASK['get_log']['success'], 'path': log_path, 'output_lines': list(output_gen)}, 200
    finally:
        return content, status


def is_admin() -> bool:
    return 'admin' in get_jwt_claims()['roles']
