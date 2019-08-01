from tensorhive.models.Task import Task, TaskStatus, try_parse_input_datetime
from tensorhive.models.User import User
from tensorhive.core import task_nursery, ssh
from tensorhive.core.task_nursery import SpawnError, ExitCodeError
from pssh.exceptions import ConnectionErrorException, AuthenticationException, UnknownHostException
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from sqlalchemy.orm.exc import NoResultFound
from tensorhive.config import API
from functools import wraps
from typing import List, Optional, Callable, Any, Dict, Tuple, Iterator
from datetime import datetime, timedelta
import logging
log = logging.getLogger(__name__)
T = API.RESPONSES['task']
S = API.RESPONSES['screen-sessions']
G = API.RESPONSES['general']
"""
This module contains two kinds of controllers:
- production-ready with authorization and authentication
- unprotected core business logic that can be used anywhere

My goal was to separate authorization from controllers' logic, so that
manual and automatic testing doesn't require patching Flask context
(@jwt_required breaks a lot of things)

In before: some controller MUST have camelCased arguments in order to keep up with API.
They are aliased to snake_case immediately inside controller body.
Connexion has this feature under the hood but it does not alsways work as it should (only in simple cases)
"""

# Typing aliases
Content = Dict[str, Any]
HttpStatusCode = int
TaskId = int


# TODO May want to move to utils
def is_admin():
    claims = get_jwt_claims()
    return 'admin' in claims['roles']


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
        assert task.host, 'hostname is empty'
        assert task.user, 'user does not exist'
        active_sessions_pids = task_nursery.running(host=task.host, user=task.user.username)
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError:
        content, status = {'msg': G['unpriviliged']}, 403
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
        results.append(task.as_dict)
    return {'msg': T['all']['success'], 'tasks': results}, 200


def business_create(task: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    """Creates new Task db record.
    Fields which require to be of datetime type are explicitly converted here.
    """
    try:
        new_task = Task(
            user_id=task['userId'],
            host=task['hostname'],
            command=task['command'],
            # TODO Adjust API spec, optional fields
            spawn_at=try_parse_input_datetime(task.get('spawnAt')),
            terminate_at=try_parse_input_datetime(task.get('terminateAt')))
        # assert all(task.values()), 'fields cannot be blank or null'
        new_task.save()
    except ValueError:
        # Invalid string format for datetime
        content, status = {'msg': G['bad_request']}, 422
    except KeyError:
        # At least one of required fields was not present
        content, status = {'msg': G['bad_request']}, 422
    except AssertionError as e:
        content, status = {'msg': T['create']['failure']['invalid'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': T['create']['success'], 'task': new_task.as_dict}, 201
    finally:
        return content, status


@synchronize_task_record
def business_get(id: TaskId) -> Tuple[Content, HttpStatusCode]:
    """Fetches one Task db record"""
    try:
        task = Task.get(id)
    except NoResultFound:
        content, status = {'msg': T['not_found']}, 404
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': T['get']['success'], 'task': task.as_dict}, 200
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
            if field_name == 'hostname':
                # API client is allowed to use more verbose name here (hostname <=> host)
                field_name = 'host'
            if field_name in {'spawnAt', 'terminateAt'}:
                field_name = field_name.replace('At', '_at')
                new_value = try_parse_input_datetime(new_value)
            else:
                # Check that every other field matches
                assert hasattr(task, field_name), 'task has no {} column'.format(field_name)
            setattr(task, field_name, new_value)
        task.save()
    except NoResultFound:
        content, status = {'msg': T['not_found']}, 404
    except ValueError:
        # Invalid string format for datetime
        content, status = {'msg': G['bad_request']}, 422
    except AssertionError as e:
        content, status = {'msg': T['update']['failure']['assertions'].format(reason=e)}, 422
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': T['update']['success'], 'task': task.as_dict}, 201
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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': T['delete']['failure']['assertions'].format(reason=e)}, 422
    except Exception:
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': T['delete']['success']}, 200
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
        content, status = {'msg': S['failure']['assertions'].format(reason=e)}, 422
    except (ConnectionErrorException, AuthenticationException, UnknownHostException) as e:
        content, status = {'msg': API.RESPONSES['ssh']['failure']['connection'].format(reason=e)}, 500
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        # FIXME
        content, status = {'msg': S['success'], 'pids': pids}, 200
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
        assert task.host, 'hostname is empty'
        assert task.user, 'user does not exist'

        pid = task_nursery.spawn(task.command, task.host, task.user.username, name_appendix=str(task.id))
        task.pid = pid
        task.status = TaskStatus.running

        # If task was scheduled to terminate and user just
        # spawned that task manually, scheduler should still
        # continue to watch and terminate the task automatically.
        task.save()
    except NoResultFound:
        content, status = {'msg': T['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': T['spawn']['failure']['assertions'].format(reason=e)}, 422
    except SpawnError as e:
        log.warning(e)
        content, status = {'msg': T['spawn']['failure']['backend'].format(reason=e)}, 500
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        log.info('Task {} is now: {}'.format(task.id, task.status.name))
        content, status = {'msg': T['spawn']['success'], 'pid': pid}, 200
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
        exit_code = task_nursery.terminate(task.pid, task.host, task.user.username, gracefully=gracefully)

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
        content, status = {'msg': T['not_found']}, 404
    except AssertionError as e:
        content, status = {'msg': T['terminate']['failure']['state'].format(reason=e)}, 409
    except ExitCodeError:
        content, status = {'msg': T['terminate']['failure']['exit_code'], 'exit_code': exit_code}, 202
    # TODO What if terminate could not connect, ConnectionErrorException?
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': T['terminate']['success'], 'exit_code': exit_code}, 200
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
        assert task.host, 'hostname is empty'
        assert task.user, 'user does not exist'
        output_gen, log_path = task_nursery.fetch_log(task.host, task.user.username, task.id, tail)
    except NoResultFound:
        content, status = {'msg': T['not_found']}, 404
    except ExitCodeError as e:
        content, status = {'msg': T['get_log']['failure']['not_found'].format(location=e)}, 404
    except AssertionError as e:
        content, status = {'msg': T['get_log']['failure']['assertions'].format(reason=e)}, 422
    except (ConnectionErrorException, AuthenticationException, UnknownHostException) as e:
        content, status = {'msg': API.RESPONSES['ssh']['failure']['connection'].format(reason=e)}, 500
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        content, status = {'msg': T['get_log']['success'], 'path': log_path, 'output_lines': list(output_gen)}, 200
    finally:
        return content, status


if __name__ == '__main__':
    """Manual testing suite for all controllers
    ONLY FOR DEVELOPMENT purposes, code is ugly and it won't be maintained for that reason
    It shows though that making CLI app for users (via real API) makes a lot of sense.
    """
    import os
    from tensorhive.database import init_db
    from inspect import cleandoc
    init_db()

    host = 'galileo.eti.pg.gda.pl'
    cmd = './long.sh'
    """
    Example: create script named long.sh
    ```
    for i in {1..60}
    do
        echo "Counting: $i"
        sleep 1s
    done
    ```
    """

    wait_for_clear = lambda: input('Press enter to show menu...')
    while True:
        print(
            cleandoc('''
            ==> Manual task controller test suite: <==

            1) Create task record
            2) Spawn one (id) or all
            3) Get one (id)
            4) Get multiple (all or by user id)
            5) Interrupt/Terminate/Kill (id)
            6) Update task command and hostname (id)
            7) Destroy task (id)
            8) Create random user with 3 tasks
            9) Destroy user (user id) - cascade deletion test
            10) Show log file (id)
            Any other key to clear console
        '''))
        action = input('> ')
        if action == '1':
            now = datetime.utcnow()
            if input('Want schedule spawn: now+20s, terminate: now+40s? (y/n) > ') == 'y':
                offset = timedelta(seconds=20)
                content, status = business_create(
                    dict(userId=1, hostname=host, command=cmd, spawnAt=now + offset, terminateAt=now + 2 * offset))
            else:
                content, status = business_create(dict(userId=1, hostname=host, command=cmd))
            print(content, status)
            print()
            print('Created with ID: ', content.get('task').get('id'))
        elif action == '2':
            task_id = input('ID or Enter for all> ')
            if task_id == '':
                content, status = get_all(userId=None, syncAll=False)
                tasks = content['tasks']
                for task in tasks:
                    content, status = business_spawn(task['id'])
                    print(content, status)
            else:
                content, status = business_spawn(int(task_id))
                print(content, status)
        elif action == '3':
            task_id = input('ID > ')
            content, status = business_get(int(task_id))
            print(content, status)
        elif action == '4':
            print('Press enter for all')
            task_id = input('User ID > ')
            sync = True if input('Want synchronized records? (y/n) > ') == 'y' else False

            if task_id:
                tasks = business_get_all(user_id=int(task_id), sync_all=sync)
            else:
                tasks = business_get_all(user_id=None, sync_all=sync)
            print('[')
            print(*tasks, sep=',\n')
            print(']')
        elif action == '5':
            task_id = input('ID > ')
            mode = input('q to interrupt, w to terminate, Enter to kill > ')
            if mode == 'q':
                gracefully = True
            elif mode == 'w':
                gracefully = None
            else:
                gracefully = False
            content, status = business_terminate(int(task_id), gracefully=gracefully)
            print(content, status)
        elif action == '6':
            task_id = input('ID > ')
            timenow = datetime.utcnow()
            content, status = business_update(
                int(task_id),
                new_values=dict(command='new_command', hostname='foobar', spawnAt=timenow, terminateAt=timenow))
            print(content, status)
        elif action == '7':
            task_id = input('ID > ')
            content, status = business_destroy(int(task_id))
            print(content, status)
        elif action == '8':
            import string
            import random
            rand_str = lambda: ''.join(random.choice(string.ascii_uppercase) for x in range(8))
            random_username, random_email = rand_str(), rand_str() + '@test.com'
            user = User(password='`123`123', email=random_email, username=random_username)
            user.save()
            for _ in range(3):
                # TODO add spawnAt, terminateAt
                content, status = business_create(dict(userId=user.id, hostname=host, command=cmd))
                print(content, status)
            print(user)
        elif action == '9':
            user_id = input('User ID > ')
            user = User.get(user_id)
            print('[BEFORE] User has {} tasks.'.format(len(user.tasks)))
            user.destroy()
            tasks_after = Task.query.filter(Task.user_id == user_id).all()
            print('[AFTER] User has now {} tasks.'.format(len(tasks_after)))
        elif action == '10':
            task_id = input('ID > ')
            if input('Request full content / Only last lines (y/Enter) > ') == 'y':
                content, status = business_get_log(int(task_id), tail=False)
            else:
                content, status = business_get_log(int(task_id), tail=True)
            print(content, status)
            print()
            print('\n'.join(content.get('output_lines') or []))
        else:
            os.system('clear')
            continue
        wait_for_clear()
        os.system('clear')
