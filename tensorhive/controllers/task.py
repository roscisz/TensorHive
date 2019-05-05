from tensorhive.models.Task import Task, TaskStatus
from tensorhive.models.User import User
from tensorhive.core import task_nursery, ssh
from tensorhive.core.task_nursery import SpawnError
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
# from tensorhive.database import flask_app
from tensorhive.config import API
from functools import wraps
from typing import List, Optional, Callable, Any, Dict
import logging
log = logging.getLogger(__name__)
T = API.RESPONSES['task']
G = API.RESPONSES['general']

# TODO print -> logging
# TODO add new responses to yml
# TODO proper content, status in every endpoint
# TODO Add @jwt_required


def synchronize(task_id: int) -> None:
    """Updates state of a Task stored in database.

    It compares current db record with list of active screen session (their pids in general)
    on node defined by Task object (task.user.username@task.host)
    """
    print('Syncing Task {}...'.format(task_id))
    try:
        task = Task.get(task_id)
        assert task.host, 'hostname is empty'
        assert task.user, 'user does not exist'
        pids = task_nursery.running(host=task.host, user=task.user.username)
    except NoResultFound:
        # This exception must be handled within try/except block when using Task.get()
        pass
    except (AssertionError, Exception) as e:
        # task_nursery.running pssh exceptions are also catched here
        print('Unable to synchronize Task {}, reason: {}'.format(task_id, e))
        task.status = TaskStatus.unsynchronized
        task.save()
        print('Task {} current status is: {}'.format(task_id, task.status))
    else:
        if task.pid in pids:
            # Nothing to do
            pass
        else:
            if task.status is TaskStatus.running:
                task.status = TaskStatus.terminated
            if task.status is TaskStatus.unsynchronized:
                task.status = TaskStatus.not_running
            task.pid = None
            task.save()
        print('Task {} current status is: {}'.format(task_id, task.status))


def synchronize_task_record(func: Callable[[int], Any]) -> Callable[[int], Any]:
    """Decorated function MUST CONTAIN task id (int), function can take more arguments though.
    If task id could not be obtained from wrapped function's arguments, synchronization will be aborted.
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
def get_all(user_id: Optional[int], sync_all: Optional[bool]) -> List[Dict]:
    # FIXME Handle exceptions etc.
    if user_id:
        tasks = Task.query.filter(Task.user_id == user_id).all()
    else:
        tasks = Task.all()

    # Wanted to decouple syncing from dict conversion with 2 oneliners (list comprehension),
    # but this code is O(n) instead of O(2n)
    results = []
    for task in tasks:
        if sync_all:
            synchronize(task.id)
        results.append(task.as_dict)
    return results, 200


# POST /tasks
def create(task):
    try:
        new_task = Task(user_id=task['userId'], host=task['hostname'], command=task['command'])
        assert all(task.values()), 'fields cannot be blank or null'
        new_task.save()
    except AssertionError as e:
        content = {'msg': T['create']['failure']['invalid'].format(reason=e)}
        status = 422
    except Exception as e:
        print(e)
        content = {'msg': G['internal_error']}
        status = 500
    else:
        content = {'msg': T['create']['success'], 'task': new_task.as_dict}
        status = 201
    finally:
        print('=================')
        return content, status


# GET /tasks/{id}
@synchronize_task_record
def get(id):
    try:
        task = Task.get(id)
    except NoResultFound:
        # FIXME
        content = {'msg': 'TODO not found'}
        status = 200
    except Exception:
        # FIXME
        content = {'msg': 'TODO Exception'}
        status = 200
    else:
        # FIXME
        content = {'msg': 'GIT TODO', 'task': task.as_dict}
        status = 200
    finally:
        print('=================')
        return content, status


# PUT /tasks/{id}:
def update(id: int, new_values: Dict[str, Any]):
    allowed_fields = {'command', 'hostname'}
    try:
        assert set(new_values.keys()).issubset(allowed_fields), 'invalid field is present'
        task = Task.get(id)

        for field_name, new_value in new_values.items():
            if field_name == 'hostname':
                # API client is allowed to use more verbose name here
                field_name = 'host'
            else:
                # Check every other field matches
                assert hasattr(task, field_name), 'task object has no {} attribute'.format(field_name)
            setattr(task, field_name, new_value)
        task.save()
    except NoResultFound:
        content = {'msg': 'TODO Not found'}
        status = 123
    # except KeyError as e:
    # FIXME Remove, won't occur
    #     content = {'msg': 'TODO Mismatche' + str(e)}
    #     status = 400
    except AssertionError as e:
        content = {'msg': 'TODO Update failure, reason: ' + str(e)}
        status = 422
    except Exception:
        content = {'msg': G['internal_error']}
        status = 500
    else:
        content = {'msg': 'TODO Update success', 'task': task.as_dict}
        status = 201
    finally:
        return content, status


# DELETE /tasks/{id}
def destroy(id: int):
    try:
        Task.get(id).destroy()
    except NoResultFound:
        # FIXME
        content = {'msg': 'TODO Not found'}
        status = 123
    except Exception as e:
        # FIXME
        content, status = {'msg': G['internal_error'] + str(e)}, 500
    else:
        # FIXME
        content, status = {'msg': 'TODO Succ deleted'}, 200
    finally:
        return content, status


# GET /screen-sessions?username=foo&hostname=bar
def screen_sessions(username: str, hostname: str) -> List[int]:
    """Returns pids of running `screen` sessions.

    This endpoint is meant for development purposes,
    there's no need to use it
    """
    try:
        assert username and hostname, 'arguments must not be empty'
        pids = task_nursery.running(host=hostname, user=username)
    except AssertionError as e:
        # FIXME
        content, status = {'msg': 'TODO running failed' + str(e), 'pids': None}, 400
    except Exception as e:
        # FIXME
        content, status = {'msg': 'TODO Exception' + str(e), 'pids': None}, 500
    else:
        # FIXME
        content, status = {'msg': T['running']['success'], 'pids': pids}, 200
    finally:
        return content, status


# GET /tasks/running?user_id=X&hostname=X
# FIXME Remove, unused - replaced by synchronization method
# FIXME Handle exceptions etc.
# def running_tasks(user_id, hostname):
#     """List of Tasks (from database) that are actually running (active screen session)"""
#     assert user_id and hostname
#     user = User.get(user_id)
#     pids = task_nursery.running(host=hostname, user=user.username)
#     tasks = Task.query.filter(Task.pid.in_(pids)).all()
#     return {'msg': T['running']['success'], 'tasks': [task.as_dict for task in tasks]}, 200


# GET /tasks/{id}/terminate
@synchronize_task_record
def terminate(id):
    try:
        task = Task.get(id)
        assert task.status is TaskStatus.running, 'Only running tasks can be terminated'
        assert task.pid, 'Task has no pid assigned'  # It means there's inconsistency
        exit_code = task_nursery.terminate(task.pid, task.host, task.user.username, gracefully=True)

        # Allow to spawn that task again
        task.pid = None
        task.status = TaskStatus.terminated
        task.save()
    except AssertionError as e:
        # FIXME
        content, status = {'msg': str(e)}, 405
    # TODO What if terminate could not connect?
    else:
        # FIXME Display success only with code==0
        if exit_code == 0:
            content, status = {'msg': T['terminate']['success'], 'exit_code': exit_code}, 123
        else:
            content, status = {'msg': 'Termination operation failed', 'exit_code': exit_code}, 200
    finally:
        return content, status


# GET /tasks/{id}/spawn
#@jwt_required
@synchronize_task_record
def spawn(id):
    # FIXME Check exceptions, etc.
    # FIXME Redesign
    try:
        task = Task.get(id)
        assert task.status is not TaskStatus.running, 'Task juz jest zespawnowany (może musisz wywołać sync)'
        assert task.command, 'command is empty'
        assert task.host, 'hostname is empty'
        assert task.user, 'user does not exist'
        print(task.as_dict)
        pid = task_nursery.spawn(task.command, task.host, task.user.username)
        task.pid = pid
        task.status = TaskStatus.running
        task.save()
    # except AssertionError as e:
    #     print(e)
    #     content, status = {
    #         'msg': T['spawn']['failure']['already_spawned']
    #     }, 405
    except NoResultFound:
        # FIXME
        content, status = {'msg': 'Task with id={} does not exist'.format(id)}, 123
    except (AssertionError, SpawnError) as e:
        # FIXME
        content, status = {'msg': 'Unable to spawn task, reason: {}'.format(e)}, 123
    except Exception as e:
        # FIXME
        content, status = str(e), 500
    else:
        content, status = {'msg': T['spawn']['success'], 'pid': pid}, 200
    finally:
        print('=================')
        return content, status


if __name__ == '__main__':
    import os
    from tensorhive.database import init_db
    init_db()

    user = '155136mm'
    host = 'galileo.eti.pg.gda.pl'
    cmd = './long.sh'  # cd ~/Simulators/095; DISPLAY= ./CarlaUE4.sh Town04'

    wait_for_clear = lambda: input('Press enter to show menu...')
    while True:
        print('''
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
        ''')
        action = input('> ')[0]
        if action == '1':
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
