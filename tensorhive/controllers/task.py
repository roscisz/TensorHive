from tensorhive.models.Task import Task, TaskStatus, try_parse_input_datetime
from tensorhive.models.User import User
from tensorhive.core import task_nursery, ssh
from tensorhive.core.task_nursery import SpawnError
from pssh.exceptions import ConnectionErrorException
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
# from tensorhive.database import flask_app
from tensorhive.config import API
from functools import wraps
from typing import List, Optional, Callable, Any, Dict, Tuple
from datetime import datetime
import logging
log = logging.getLogger(__name__)
T = API.RESPONSES['task']
S = API.RESPONSES['screen-sessions']
G = API.RESPONSES['general']

# TODO print -> logging everywhere
# TODO add new responses to yml
# TODO proper content, status in every endpoint
# TODO Add @jwt_required
# TODO Add security bearer to endpoints in API spec
# TODO Check priviliges
# TODO Add descriptions to boring CRUD functions
Content = Dict[str, Any]
HttpStatusCode = int
TaskId = int


class ExitCodeError(AssertionError):
    pass


# TODO Move somewhere else
def synchronize(task_id: TaskId) -> None:
    """Updates state of a Task object stored in database.

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
    print('Syncing Task {}...'.format(task_id))
    try:
        task = Task.get(task_id)
        assert task.host, 'hostname is empty'
        assert task.user, 'user does not exist'
        active_sessions_pids = task_nursery.running(host=task.host, user=task.user.username)
    except NoResultFound:
        # This exception must be handled within try/except block when using Task.get()
        pass
    except (AssertionError, Exception) as e:
        # task_nursery.running pssh exceptions are also catched here
        print('Unable to synchronize Task {}, reason: {}'.format(task_id, e))
        print('Task {} status was: {}'.format(task_id, task.status.name))
        task.status = TaskStatus.unsynchronized
        task.save()
        print('Task {} is now: {}'.format(task_id, task.status.name))
    else:
        print('[BEFORE SYNC] Task {} status was: {}'.format(task_id, task.status.name))
        change_status_msg = '[AFTER SYNC] Task {id} is now: {curr_status}'
        if task.pid not in active_sessions_pids:
            if task.status is TaskStatus.running:
                task.status = TaskStatus.terminated
                print(change_status_msg.format(id=task_id, curr_status=task.status.name))
            if task.status is TaskStatus.unsynchronized:
                task.status = TaskStatus.not_running
                print(change_status_msg.format(id=task_id, curr_status=task.status.name))
            task.pid = None
            task.save()


def synchronize_task_record(func: Callable[[int], Any]) -> Callable[[int], Any]:
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
            print('Synchronization aborted!')
            print('Task id not found in {}(), args: {}, kwargs: {}'.format(func.__name__, args, kwargs))
        return func(*args, **kwargs)

    return sync_wrapper


# FIXME Maybe camelCased arguments? (API client standpoint)
#  GET /tasks?user_id=X?sync_all=1
# FIXME Revert @jwt_required
def get_all(user_id: Optional[int], sync_all: Optional[bool]) -> List[Dict]:
    """Fetches either all Task records or only those in relation with specific user.
    Allows for synchronizing state of each Task out-of-the-box.

    In typical scenario API client would want to get all records without sync and
    then run sync each records individually.
    """
    # FIXME Exceptions should never occur, but need to experiment more
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


# POST /tasks
# FIXME Revert @jwt_required
def create(task: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    """Creates new Task db record.
    Fields which require to be of datetime type are explicitly converted here.
    """
    try:
        new_task = Task(
            user_id=task['userId'],
            host=task['hostname'],
            command=task['command'],
            # TODO Adjust API spec, optional fields
            spawn_at=try_parse_input_datetime(task.get('spawn_at')),
            terminate_at=try_parse_input_datetime(task.get('terminate_at')))
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
        print('=================')
        return content, status


# GET /tasks/{id}
# FIXME Revert @jwt_required
@synchronize_task_record
def get(id: TaskId) -> Tuple[Content, HttpStatusCode]:
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


# PUT /tasks/{id}
# FIXME Revert @jwt_required
# FIXME Check if task belongs to user! (403, unpriviliged)
# TODO What if task is already running: should we allow for updating command, hostname, etc. Currently it should affect only next usess
def update(id: TaskId, new_values: Dict[str, Any]) -> Tuple[Content, HttpStatusCode]:
    """Updates certain fields of a Task db record, see `allowed_fields`."""
    allowed_fields = {'command', 'hostname', 'spawn_at', 'terminate_at'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        task = Task.get(id)

        for field_name, new_value in new_values.items():
            if field_name == 'hostname':
                # API client is allowed to use more verbose name here (hostname <=> host)
                field_name = 'host'
            if field_name in {'spawn_at', 'terminate_at'}:
                new_value = try_parse_input_datetime(new_value)
            else:
                # Check that every other field matches
                assert hasattr(task, field_name), 'task object has no {} attribute'.format(field_name)
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


# DELETE /tasks/{id}
# FIXME Revert @jwt_required
# FIXME Check if task belongs to user (id from JWT)! (403, unpriviliged)
# TODO Maybe wen don't need to synchronize? (but I think we need to terminate task first)
@synchronize_task_record
def destroy(id: TaskId) -> Tuple[Content, HttpStatusCode]:
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
    except ConnectionErrorException as e:
        # Dev note:
        # There are much more pssh.exceptions to handle, but treating them all as
        # built-in Exception should be sufficient, API client does not require to have full knowledge.
        log.error(e)
        content, status = {'msg': API.RESPONSES['ssh']['failure']['connection']}, 404
    except Exception as e:
        log.critical(e)
        content, status = {'msg': G['internal_error']}, 500
    else:
        # FIXME
        content, status = {'msg': S['success'], 'pids': pids}, 200
    finally:
        return content, status


# GET /tasks/{id}/terminate
# FIXME Revert @jwt_required
@synchronize_task_record
def terminate(id: TaskId) -> Tuple[Content, HttpStatusCode]:
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

        exit_code = task_nursery.terminate(task.pid, task.host, task.user.username, gracefully=True)

        if exit_code != 0:
            raise ExitCodeError('operation exit code is not 0')

        # Allow to spawn that task again
        task.pid = None
        task.status = TaskStatus.terminated
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
        print('Task {} is now: {}'.format(task.id, task.status.name))
        content, status = {'msg': T['terminate']['success'], 'exit_code': exit_code}, 200
    finally:
        return content, status


# GET /tasks/{id}/spawn
# FIXME Revert @jwt_required
@synchronize_task_record
def spawn(id: TaskId) -> Tuple[Content, HttpStatusCode]:
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
        pid = task_nursery.spawn(task.command, task.host, task.user.username)
        task.pid = pid
        task.status = TaskStatus.running

        # If task was scheduled to terminate and user just
        # spawned that task manually, scheduler should still
        #  continue to watch and terminate the task automatically.
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
        print('Task {} is now: {}'.format(task.id, task.status.name))
        content, status = {'msg': T['spawn']['success'], 'pid': pid}, 200
    finally:
        return content, status


if __name__ == '__main__':
    import os
    from tensorhive.database import init_db
    from inspect import cleandoc
    init_db()

    user = '155136mm'
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
            2) Spawn (id)
            3) Get one (id)
            4) Get multiple (all or by user id)
            5) Terminate (id)
            6) Update task command and hostname (id)
            7) Destroy task (id)
            8) Create random user with 3 tasks
            9) Destroy user (user id) - cascade deletion test
            Any other key to clear console
        '''))
        action = input('> ')[0]
        if action == '1':
            from datetime import datetime, timedelta
            now = datetime.utcnow()
            if input('Want schedule spawn: now-20s, terminate: now+20s? (y/n) > ') == 'y':
                offset = timedelta(seconds=20)
                content, status = create(
                    dict(userId=1, hostname=host, command=cmd, spawnAt=now - offset, terminateAt=now + offset))
            else:
                content, status = create(dict(userId=1, hostname=host, command=cmd))
            print(content, status)
        elif action == '2':
            task_id = input('ID > ')
            content, status = spawn(int(task_id))
            print(content, status)
        elif action == '3':
            task_id = input('ID > ')
            task = get(int(task_id))
            print(task)
        elif action == '4':
            print('Press enter for all')
            task_id = input('User ID > ')
            sync = True if input('Want synchronized records? (y/n) > ') == 'y' else False

            if task_id:
                tasks = get_all(user_id=int(task_id), sync_all=sync)
            else:
                tasks = get_all(user_id=None, sync_all=sync)
            print('[')
            print(*tasks, sep=',\n')
            print(']')
        elif action == '5':
            task_id = input('ID > ')
            content, status = terminate(int(task_id))
            print(content, status)
        elif action == '6':
            task_id = input('ID > ')
            content, status = update(int(task_id), new_values=dict(command='new_command', hostname='miczi.gda.pl'))
            print(content, status)
        elif action == '7':
            task_id = input('ID > ')
            content, status = destroy(int(task_id))
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
                content, status = create(dict(userId=user.id, hostname=host, command=cmd))
                print(content, status)
            print(user)
        elif action == '9':
            user_id = input('User ID > ')
            user = User.get(user_id)
            print('[BEFORE] User has {} tasks.'.format(len(user.tasks)))
            user.destroy()
            tasks_after = Task.query.filter(Task.user_id == user_id).all()
            print('[AFTER] User has now {} tasks.'.format(len(tasks_after)))
        else:
            os.system('clear')
            continue
        wait_for_clear()
        os.system('clear')
