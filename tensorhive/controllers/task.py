from tensorhive.models.Task import Task, TaskStatus
from tensorhive.models.User import User
from tensorhive.core import task_nursery, ssh
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
            task.pid = None
            task.save()
        print('Task {} current status is: {}'.format(task_id, task.status))


def synchronize_task_record(func) -> Callable[[int], Any]:
    """Decorated function MUST CONTAIN task id (int).
    (function can take more arguments though)
    """

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            task_id = args[0]
        except IndexError:
            task_id = kwargs.get('id') or kwargs.get('task_id') or kwargs.get('taskId')

        print('AAAAAAAAAAAAA', task_id)
        if task_id:
            synchronize(task_id)
        return func(*args, **kwargs)

    return sync_wrapper


# FIXME Case
#  GET /tasks?user_id=X?syncall=1
def get_all(user_id: Optional[int], sync_all: Optional[bool]) -> List[Dict]:
    """"""
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
        content = {'msg': 'BAD TODO'}
        status = 123
    else:
        content = {'msg': 'GIT TODO', 'task': task.as_dict}
        status = 123
    finally:
        print('=================')
        return content, status


# PUT /tasks/{id}:
def update(id):
    raise NotImplementedError


# DELETE /tasks/{id}
def destroy():
    raise NotImplementedError


# FIXME Unused: screen-specific endpoint
def running_sessions(user_id, hostname):
    try:
        assert user_id and hostname
        # TODO Maybe ORM objects should be updated here
        user = User.get(user_id)
        pids = task_nursery.running(host=hostname, user=user.username)
    except AssertionError:
        raise NotImplementedError
    except Exception:
        raise NotImplementedError
    else:
        content, status = {'msg': T['running']['success'], 'pids': pids}, 200
    finally:
        return content, status
        

# GET /tasks/{id}/terminate
def terminate(id):
    # FIXME Check for pid being None
    try:
        task = Task.get(id)
        assert task.pid and task.exit_code is None
        exit_code = task_nursery.terminate(task.pid, task.host, task.user.username)

        # Allow to spawn that object again
        task.pid = None
        task.exit_code = exit_code
        task.save()
    except AssertionError:
        content, status = {'msg': T['terminate']['failure']['invalid_state']}, 405
    except AssertionError:
        raise NotImplementedError
    else:
        # FIXME Display success only with code==0
        content, status = {'msg': T['terminate']['success'], 'exit_code': exit_code}, 200
    finally:
        return content, status

# GET /tasks/{id}/start
#@jwt_required
def spawn(id):
    # FIXME Check exceptions, etc.
    # FIXME Redesign
    try:
        task = Task.get(id)
        assert task.pid is None
        pid = task_nursery.spawn(task.command, task.host, task.user.username)
        task.pid = pid
        task.exit_code = None
        task.save()
    except AssertionError:
        content, status = {'msg': T['spawn']['failure']['already_spawned']}, 405    
    except AssertionError:
        raise NotImplementedError
    else:
        content, status = {'msg': T['spawn']['success'], 'pid': pid}, 200
    finally:
        return content, status

